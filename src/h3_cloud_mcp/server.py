"""stdio MCP tools for a private, rented ComfyUI instance."""

from __future__ import annotations

import os

from mcp.server import MCPServer

from . import comfy
from .workflow import build_t2va

mcp = MCPServer("H3 Cloud MCP")


@mcp.tool()
def h3_check_backend() -> dict:
    """Read the private ComfyUI system status before submitting paid GPU work."""
    system = comfy.request("GET", "/system_stats")
    nodes = comfy.request("GET", "/object_info")
    required = ("MiniMaxH3ImageToVideo", "VAEDecodeAudio", "CreateVideo", "SaveVideo")
    missing = [name for name in required if name not in nodes]
    models = (
        ("UNETLoader", "unet_name", os.getenv("H3_MODEL", "minimax_h3_fl2va_pruned_int8_convrot.safetensors")),
        ("CLIPLoader", "clip_name", os.getenv("H3_TEXT_ENCODER", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors")),
        ("VAELoader", "vae_name", os.getenv("H3_VIDEO_VAE", "minimax_h3_video_vae_fp16.safetensors")),
        ("VAELoader", "vae_name", os.getenv("H3_AUDIO_VAE", "minimax_h3_audio_vae_fp32.safetensors")),
    )
    missing_models = []
    for node, key, filename in models:
        choices = nodes.get(node, {}).get("input", {}).get("required", {}).get(key, [[]])[0]
        if filename not in choices:
            missing_models.append(filename)
    return {"reachable": True, "devices": system.get("devices", []),
            "comfyui_version": system.get("system", {}).get("comfyui_version"),
            "h3_nodes_ready": not missing, "missing_nodes": missing,
            "h3_models_ready": not missing_models, "missing_models": missing_models}


@mcp.tool()
def h3_generate(prompt: str, width: int = 768, height: int = 448,
                frames: int = 124, steps: int = 20, seed: int | None = None) -> dict:
    """Queue a MiniMax H3 text-to-video clip with generated stereo audio; returns job_id immediately."""
    graph = build_t2va(prompt, width, height, frames, steps, seed)
    return comfy.submit(graph)


@mcp.tool()
def h3_job_status(job_id: str) -> dict:
    """Check whether a queued H3 video has finished and list its ComfyUI output files."""
    return comfy.status(job_id)


@mcp.tool()
def h3_download_video(job_id: str) -> dict:
    """Download a finished H3 video through the private tunnel into H3_OUTPUT_DIR."""
    return comfy.download(job_id)


@mcp.tool()
def h3_cancel_job(job_id: str) -> dict:
    """Remove a queued H3 job or request interruption of that exact running job."""
    return comfy.cancel(job_id)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
