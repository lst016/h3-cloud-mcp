"""Minimal ComfyUI HTTP client. Connect through a local SSH tunnel."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import httpx


def base_url() -> str:
    url = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("COMFYUI_URL must be a local HTTP address; use an SSH tunnel")
    return url


def request(method: str, path: str, **kwargs: object) -> dict:
    with httpx.Client(base_url=base_url(), timeout=30) as client:
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()


def submit(graph: dict) -> dict:
    result = request("POST", "/prompt", json={"prompt": graph})
    if "prompt_id" not in result:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {result}")
    return {"job_id": result["prompt_id"], "queue_number": result.get("number"), "node_errors": result.get("node_errors", {})}


def status(job_id: str) -> dict:
    if not job_id or any(c not in "0123456789abcdef-" for c in job_id.lower()) or len(job_id) > 64:
        raise ValueError("invalid job_id")
    history = request("GET", f"/history/{job_id}")
    if job_id in history:
        entry = history[job_id]
        videos = []
        for output in entry.get("outputs", {}).values():
            videos.extend(output.get("videos", []))
        state = entry.get("status", {}).get("status_str", "completed")
        return {"job_id": job_id, "state": state, "videos": videos,
                "messages": entry.get("status", {}).get("messages", [])[-3:]}
    queue = request("GET", "/queue")
    for name, state in (("queue_running", "running"), ("queue_pending", "queued")):
        if any(len(item) > 1 and item[1] == job_id for item in queue.get(name, [])):
            return {"job_id": job_id, "state": state, "videos": []}
    return {"job_id": job_id, "state": "unknown", "videos": []}


def download(job_id: str) -> dict:
    result = status(job_id)
    if result["state"] not in ("success", "completed") or not result["videos"]:
        raise ValueError("job has no completed video yet")
    video = result["videos"][0]
    filename = video.get("filename", "")
    if not filename or Path(filename).name != filename:
        raise ValueError("invalid ComfyUI output filename")
    output_dir = Path(os.getenv("H3_OUTPUT_DIR", str(Path.cwd() / "outputs"))).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{job_id}-{filename}"
    params = {"filename": filename, "subfolder": video.get("subfolder", ""), "type": video.get("type", "output")}
    with httpx.Client(base_url=base_url(), timeout=120) as client:
        with client.stream("GET", "/view", params=params) as response:
            response.raise_for_status()
            with target.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
    return {"job_id": job_id, "path": str(target), "bytes": target.stat().st_size}
