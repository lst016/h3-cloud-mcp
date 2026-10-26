#!/usr/bin/env bash
set -euo pipefail

# Run on the cloud instance after installing the official Hugging Face CLI.
# Model files are written directly to the AutoDL data disk, not the system disk.
MODEL_DIR="${H3_MODEL_DIR:-/root/autodl-tmp/h3-models}"
COMFY_DIR="${COMFY_DIR:-/root/ComfyUI}"
REVISION="fd70b39279d1ae6eb214c903f53e1bec3af19a77"

command -v hf >/dev/null || { echo "Install huggingface_hub CLI first: python -m pip install -U huggingface_hub" >&2; exit 1; }
test -d "$COMFY_DIR/models" || { echo "ComfyUI models directory not found: $COMFY_DIR/models" >&2; exit 1; }
mkdir -p "$MODEL_DIR" "$COMFY_DIR/models/diffusion_models" "$COMFY_DIR/models/text_encoders" "$COMFY_DIR/models/vae"

hf download Comfy-Org/MiniMax-H3 \
  --revision "$REVISION" \
  --include \
    'diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors' \
    'text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors' \
    'vae/minimax_h3_video_vae_fp16.safetensors' \
    'vae/minimax_h3_audio_vae_fp32.safetensors' \
  --local-dir "$MODEL_DIR"

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
echo "Four H3 files are linked. Verify them and run a real ComfyUI smoke test before claiming success."
