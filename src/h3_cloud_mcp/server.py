"""stdio MCP tools for managed AutoDL Art and private ComfyUI H3 workflows."""

from __future__ import annotations

import os
import logging

from mcp.server import MCPServer

from . import art_api, comfy
from .workflow import build_t2va

mcp = MCPServer("H3 Cloud MCP")


@mcp.tool()
def h3_art_quote(duration: int = 5, resolution: str = "480p横") -> dict:
    """Estimate AutoDL Art managed H3 price using rates observed 2026-10-26; no charge."""
    return art_api.quote(duration, resolution)


@mcp.tool()
def h3_art_list_workflows() -> list[dict]:
    """List 18 reviewed AutoDL Art H3 workflows, categories, media requirements and resolutions."""
    return art_api.list_workflows()


@mcp.tool()
def h3_art_quote_workflow(workflow_id: str, duration: int = 5, resolution: str | None = None) -> dict:
    """Estimate one selected H3 workflow using observed rates; no charge or live price lookup."""
    return art_api.quote_workflow(workflow_id, duration, resolution)


@mcp.tool()
def h3_art_generate(prompt: str, duration: int = 5, resolution: str = "480p横", seed: int | None = None) -> dict:
    """Submit one paid managed H3 text-to-video task; requires AUTODL_ART_TOKEN and H3_ART_ENABLE_PAID=1."""
    return art_api.generate(prompt, duration, resolution, seed)


@mcp.tool()
def h3_art_generate_workflow(workflow_id: str, prompt: str = "", duration: int = 5,
                             resolution: str | None = None, images: list[str] | None = None,
                             audios: list[str] | None = None, first_frame: str | None = None,
                             last_frame: str | None = None, mode: str | None = None,
                             seed: int | None = None) -> dict:
    """Submit one allowlisted paid H3 workflow. Media must be public HTTPS URLs; no local file upload."""
    return art_api.generate_workflow(workflow_id, prompt, duration, resolution, images,
                                     audios, first_frame, last_frame, mode, seed)


@mcp.tool()
def h3_art_job_status(task_id: str) -> dict:
    """Check any managed H3 task status. processing_seconds is task time, not clip length."""
    return art_api.status(task_id)


@mcp.tool()
def h3_art_download_video(task_id: str) -> dict:
    """Download a completed managed H3 MP4 into H3_OUTPUT_DIR."""
    return art_api.download(task_id)


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
    # Signed output URLs must not appear in MCP stderr logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
