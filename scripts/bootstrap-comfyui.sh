#!/usr/bin/env bash
set -euo pipefail

# Install a pinned ComfyUI checkout without changing the image's CUDA/PyTorch stack.
COMFY_DIR="${COMFY_DIR:-/root/ComfyUI}"
DATA_DIR="${H3_DATA_DIR:-/root/autodl-tmp}"
COMMIT="fe298e4e20f1ff26d30e8639267bbd0b57811390"
PYTHON="${H3_PYTHON:-python}"

command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
"$PYTHON" - <<'PY'
import torch

assert torch.cuda.is_available(), "CUDA is unavailable"
capability = torch.cuda.get_device_capability(0)
arch = f"sm_{capability[0]}{capability[1]}"
assert capability >= (12, 0), f"This NVFP4 preset needs Blackwell; found {arch}"
assert arch in torch.cuda.get_arch_list(), f"Installed PyTorch has no {arch} kernels"
print(torch.__version__, "CUDA", torch.version.cuda, torch.cuda.get_device_name(0), arch)
PY
mkdir -p "$DATA_DIR"

if test ! -d "$COMFY_DIR"; then
  archive="$DATA_DIR/ComfyUI-$COMMIT.zip"
  curl --fail --location --proto '=https' --proto-redir '=https' --retry 8 --retry-delay 5 --output "$archive.part" \
    "https://codeload.github.com/comfyanonymous/ComfyUI/zip/$COMMIT"
  mv "$archive.part" "$archive"
  "$PYTHON" - "$archive" "$COMFY_DIR" "$COMMIT" <<'PY'
import pathlib
import sys
import zipfile

archive, destination, commit = sys.argv[1:]
destination = pathlib.Path(destination)
with zipfile.ZipFile(archive) as package:
    package.extractall(destination.parent)
(destination.parent / f"ComfyUI-{commit}").rename(destination)
PY
fi

test -f "$COMFY_DIR/requirements.txt" || { echo "ComfyUI checkout is incomplete: $COMFY_DIR" >&2; exit 1; }
"$PYTHON" -m pip install -r "$COMFY_DIR/requirements.txt"
"$PYTHON" -c 'import torch, comfyui_frontend_package; print("ComfyUI dependencies ready; CUDA:", torch.cuda.is_available())'
echo "ComfyUI source is ready at $COMFY_DIR. Run download-models.sh next."
