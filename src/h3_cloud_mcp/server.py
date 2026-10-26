"""stdio MCP tools for a private, rented ComfyUI instance."""

from __future__ import annotations

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
    return {"reachable": True, "devices": system.get("devices", []),
            "comfyui_version": system.get("system", {}).get("comfyui_version"),
            "h3_nodes_ready": not missing, "missing_nodes": missing}


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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
