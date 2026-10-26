#!/usr/bin/env bash
set -euo pipefail

# Model files are written directly to the AutoDL data disk, not the system disk.
MODEL_DIR="${H3_MODEL_DIR:-/root/autodl-tmp/h3-models}"
COMFY_DIR="${COMFY_DIR:-/root/ComfyUI}"
REVISION="fd70b39279d1ae6eb214c903f53e1bec3af19a77"
ORIGIN="${H3_DOWNLOAD_ORIGIN:-https://huggingface.co}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

[[ "$ORIGIN" == https://* ]] || { echo "H3_DOWNLOAD_ORIGIN must use HTTPS" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum is required" >&2; exit 1; }
test -d "$COMFY_DIR/models" || { echo "ComfyUI models directory not found: $COMFY_DIR/models" >&2; exit 1; }
mkdir -p "$MODEL_DIR" "$COMFY_DIR/models/diffusion_models" "$COMFY_DIR/models/text_encoders" "$COMFY_DIR/models/vae"

while read -r expected file; do
  target="$MODEL_DIR/$file"
  if test -f "$target"; then
    actual="$(sha256sum "$target")"
    [[ "${actual%% *}" == "$expected" ]] || { echo "Checksum mismatch: $file" >&2; exit 1; }
    echo "Verified: $file"
    continue
  fi
  mkdir -p "$(dirname "$target")"
  partial="$target.part"
  if ! curl --fail --location --proto '=https' --proto-redir '=https' --continue-at - --retry 8 --retry-delay 5 \
    --connect-timeout 20 --output "$partial" \
    "${ORIGIN%/}/Comfy-Org/MiniMax-H3/resolve/$REVISION/$file"; then
    if test -f "$partial"; then
      actual="$(sha256sum "$partial")"
      if [[ "${actual%% *}" == "$expected" ]]; then
        mv "$partial" "$target"
        echo "Verified: $file"
        continue
      fi
    fi
    echo "Download stopped; rerun to resume: $file" >&2
    exit 1
  fi
  actual="$(sha256sum "$partial")"
  if [[ "${actual%% *}" != "$expected" ]]; then
    bad="$partial.bad.$(date +%s).$$"
    mv "$partial" "$bad"
    echo "Checksum mismatch: $file; corrupt download moved to $bad" >&2
    exit 1
  fi
  mv "$partial" "$target"
  echo "Verified: $file"
done < "$SCRIPT_DIR/model-sha256.txt"

for file in \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors; do
  test -s "$MODEL_DIR/$file" || { echo "Missing model: $file" >&2; exit 1; }
  link="$COMFY_DIR/models/$file"
  if test -e "$link" && ! test "$link" -ef "$MODEL_DIR/$file"; then
    echo "Existing different model at $link; leaving it untouched" >&2
    exit 1
  fi
  if ! test -e "$link"; then ln -s "$MODEL_DIR/$file" "$link"; fi
done
echo "Four H3 files passed SHA-256 and are linked. Run a real ComfyUI smoke test before claiming success."
