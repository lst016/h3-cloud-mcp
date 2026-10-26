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
    with httpx.Client(base_url=base_url(), timeout=30, trust_env=False) as client:
        response = client.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"ComfyUI {method} {path} returned {response.status_code}: {response.text[:4096]}") from exc
        return response.json() if response.content else {}


def submit(graph: dict) -> dict:
    queue = request("GET", "/queue")
    active = len(queue.get("queue_running", [])) + len(queue.get("queue_pending", []))
    max_active = int(os.getenv("H3_MAX_ACTIVE_JOBS", "1"))
    if not 1 <= max_active <= 4:
        raise ValueError("H3_MAX_ACTIVE_JOBS must be between 1 and 4")
    if active >= max_active:
        raise RuntimeError(f"ComfyUI has {active} active job(s); limit is {max_active}")
    result = request("POST", "/prompt", json={"prompt": graph})
    if "prompt_id" not in result:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {result}")
    return {"job_id": result["prompt_id"], "queue_number": result.get("number"), "node_errors": result.get("node_errors", {})}


def validate_job_id(job_id: str) -> None:
    if not job_id or any(c not in "0123456789abcdef-" for c in job_id.lower()) or len(job_id) > 64:
        raise ValueError("invalid job_id")


def status(job_id: str) -> dict:
    validate_job_id(job_id)
    history = request("GET", f"/history/{job_id}")
    if job_id in history:
        entry = history[job_id]
        videos = []
        for output in entry.get("outputs", {}).values():
            # ComfyUI SaveVideo reports MP4 files under "images" via PreviewVideo.
            for item in output.get("videos", []) + output.get("images", []):
                if item.get("filename", "").lower().endswith((".mp4", ".mkv", ".webm")):
                    videos.append(item)
        state = entry.get("status", {}).get("status_str", "completed")
        return {"job_id": job_id, "state": state, "videos": videos,
                "messages": entry.get("status", {}).get("messages", [])[-3:]}
    queue = request("GET", "/queue")
    for name, state in (("queue_running", "running"), ("queue_pending", "queued")):
        if any(len(item) > 1 and item[1] == job_id for item in queue.get(name, [])):
            return {"job_id": job_id, "state": state, "videos": []}
    return {"job_id": job_id, "state": "unknown", "videos": []}


def cancel(job_id: str) -> dict:
    validate_job_id(job_id)
    queue = request("GET", "/queue")
    if any(len(item) > 1 and item[1] == job_id for item in queue.get("queue_pending", [])):
        request("POST", "/queue", json={"delete": [job_id]})
        return {"job_id": job_id, "action": "removed_from_queue"}
    if any(len(item) > 1 and item[1] == job_id for item in queue.get("queue_running", [])):
        request("POST", "/interrupt", json={"prompt_id": job_id})
        return {"job_id": job_id, "action": "interrupt_requested"}
    return {"job_id": job_id, "action": "not_active"}


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
    with httpx.Client(base_url=base_url(), timeout=120, trust_env=False) as client:
        with client.stream("GET", "/view", params=params) as response:
            response.raise_for_status()
            with target.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
    return {"job_id": job_id, "path": str(target), "bytes": target.stat().st_size}
