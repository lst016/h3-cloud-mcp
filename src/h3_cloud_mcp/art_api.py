"""AutoDL Art managed MiniMax H3 workflow. No rented instance is needed."""

from __future__ import annotations

import ipaddress
import os
import socket
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID
from zoneinfo import ZoneInfo

import httpx

from .art_workflows import catalog, get_workflow, resolution_for

BASE = "https://autodl.art"
WORKFLOW = "minimax_h3_lightx2v_no_pic"
RESOLUTIONS = set(get_workflow(WORKFLOW).resolutions)
# AutoDL Art currently returns a signed video URL on this Volcengine TOS host.
# A local proxy may map it to a synthetic 198.18.0.0/15 DNS address.
TRUSTED_OUTPUT_HOSTS = {"cg-comfyui-prod.tos-cn-beijing.volces.com"}
_submitted = 0
_submission_lock = threading.Lock()


def _validate(prompt: str, duration: int, resolution: str, seed: int | None) -> None:
    if not prompt or not prompt.strip() or len(prompt) > 20000:
        raise ValueError("prompt must contain 1 to 20000 characters")
    if type(duration) is not int or not 1 <= duration <= 15:
        raise ValueError("duration must be an integer between 1 and 15 seconds")
    if resolution not in RESOLUTIONS:
        raise ValueError(f"resolution must be one of: {', '.join(sorted(RESOLUTIONS))}")
    if seed is not None and (type(seed) is not int or not 1 <= seed <= 999_999_999_999_999):
        raise ValueError("seed must be an integer from 1 to 999999999999999")


def quote(duration: int = 5, resolution: str = "480p横") -> dict:
    _validate("quote", duration, resolution, None)
    return quote_workflow(WORKFLOW, duration, resolution)


def quote_workflow(workflow_id: str, duration: int = 5, resolution: str | None = None) -> dict:
    """Estimate one output clip using a reviewed workflow's observed rates; no API call."""
    spec = get_workflow(workflow_id)
    if type(duration) is not int or not 1 <= duration <= spec.max_seconds:
        raise ValueError(f"duration for {workflow_id} must be an integer from 1 to {spec.max_seconds}")
    alias, provider_resolution = resolution_for(spec, resolution)
    tier = alias.split("p", 1)[0] + "p"
    peak_rate, offpeak_rate = spec.rates[tier]
    hour = datetime.now(ZoneInfo("Asia/Shanghai")).hour
    window = "offpeak" if hour < 8 else "peak"
    return {
        "workflow_id": workflow_id,
        "duration_seconds": duration,
        "resolution": alias,
        "provider_resolution": provider_resolution,
        "pricing_window_china": window,
        "estimated_cny": round(duration * (offpeak_rate if window == "offpeak" else peak_rate), 2),
        "worst_observed_cny": round(duration * peak_rate, 2),
        "rate_observed_on": "2026-10-26",
        "warning": "Static estimate only; verify this workflow's current AutoDL Art price before paid submission.",
    }


def list_workflows() -> list[dict]:
    """Return the reviewed workflow allowlist and parameter limits without a paid request."""
    return catalog()


def _token() -> str:
    token = os.getenv("AUTODL_ART_TOKEN", "").strip()
    if not token:
        raise RuntimeError("AUTODL_ART_TOKEN is missing; create a ComfyUI-group token in AutoDL Art")
    return token


def _api(method: str, path: str, *, body: dict | None = None) -> dict:
    headers = {"Authorization": _token(), "Content-Type": "application/json"}
    try:
        with httpx.Client(base_url=BASE, timeout=30, follow_redirects=False) as client:
            response = client.request(method, path, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        # Never echo response bodies: upstream may include credential-like data.
        raise RuntimeError(f"AutoDL Art {method} request failed: {type(exc).__name__}") from exc
    if payload.get("code") != "Success" or not isinstance(payload.get("data"), dict):
        raise RuntimeError(f"AutoDL Art API rejected request (code={payload.get('code')!r})")
    return payload["data"]


def _task_id(task_id: str) -> str:
    try:
        return str(UUID(task_id))
    except (ValueError, AttributeError) as exc:
        raise ValueError("invalid AutoDL Art task_id") from exc


def generate(prompt: str, duration: int = 5, resolution: str = "480p横", seed: int | None = None) -> dict:
    """Backward-compatible text-to-video shortcut for the verified workflow."""
    _validate(prompt, duration, resolution, seed)
    return generate_workflow(WORKFLOW, prompt, duration, resolution, seed=seed)


def _media_url(value: str, name: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 4096:
        raise ValueError(f"{name} must be a nonempty HTTPS URL")
    parsed = urlparse(value)
    host = parsed.hostname
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
        raise ValueError(f"{name} must be a public HTTPS URL without credentials or fragment")
    if parsed.port not in (None, 443) or host.lower() == "localhost" or host.endswith(".localhost"):
        raise ValueError(f"{name} must be a public HTTPS URL")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError(f"{name} must use a public address")
    return value


def _media_list(values: list[str] | None, name: str, minimum: int, maximum: int) -> list[str]:
    if values is None:
        values = []
    if not isinstance(values, list) or not minimum <= len(values) <= maximum:
        raise ValueError(f"{name} must contain {minimum} to {maximum} HTTPS URLs")
    return [_media_url(value, f"{name}[{index}]") for index, value in enumerate(values)]


def generate_workflow(workflow_id: str, prompt: str = "", duration: int = 5,
                      resolution: str | None = None, images: list[str] | None = None,
                      audios: list[str] | None = None, first_frame: str | None = None,
                      last_frame: str | None = None, mode: str | None = None,
                      seed: int | None = None) -> dict:
    """Submit one allowlisted H3 workflow using its reviewed input schema.

    Media inputs are public HTTPS URLs. This does not upload local files.
    """
    global _submitted
    spec = get_workflow(workflow_id)
    estimate = quote_workflow(workflow_id, duration, resolution)
    if not isinstance(prompt, str) or len(prompt) > spec.prompt_limit or (spec.prompt_required and not prompt.strip()):
        raise ValueError(f"prompt for {workflow_id} must contain 1 to {spec.prompt_limit} characters")
    if not spec.prompt_required and prompt:
        raise ValueError(f"{workflow_id} does not accept a prompt")
    image_urls = _media_list(images, "images", spec.min_images, spec.max_images)
    audio_urls = _media_list(audios, "audios", spec.min_audios, spec.max_audios)
    if spec.first_last:
        first = _media_url(first_frame, "first_frame")
        last = _media_url(last_frame, "last_frame")
    elif first_frame is not None or last_frame is not None:
        raise ValueError(f"{workflow_id} does not accept first_frame or last_frame")
    if mode is not None:
        if not spec.mode or mode not in ("高速模式", "高质模式"):
            raise ValueError("mode must be 高速模式 or 高质模式 for workflows 801/802/803")
    if seed is not None:
        if not spec.seed or type(seed) is not int or not 1 <= seed <= 999_999_999_999_999:
            raise ValueError("seed must be an integer from 1 to 999999999999999 for this workflow")
    body = {"resolution": estimate["provider_resolution"]}
    if spec.prompt_required:
        body["prompt"] = prompt
    body["audio_duration" if spec.audio_duration else "duration"] = duration
    for index, url in enumerate(image_urls):
        body[f"ref_image_{index}"] = url
    for index, url in enumerate(audio_urls):
        body[f"ref_audio_{index}"] = url
    if spec.first_last:
        body.update({"first_frame": first, "last_frame": last})
    if mode is not None:
        body["mode"] = mode
    if seed is not None:
        body["seed"] = seed
    if os.getenv("H3_ART_ENABLE_PAID") != "1":
        raise RuntimeError("Paid submission is disabled; set H3_ART_ENABLE_PAID=1 after checking the live price")
    limit = float(os.getenv("H3_ART_MAX_ESTIMATED_CNY", "0.25"))
    if not 0 < limit <= 50:
        raise ValueError("H3_ART_MAX_ESTIMATED_CNY must be > 0 and <= 50")
    if estimate["worst_observed_cny"] > limit:
        raise ValueError(f"observed peak-price estimate ¥{estimate['worst_observed_cny']:.2f} exceeds configured limit ¥{limit:.2f}")
    max_tasks = int(os.getenv("H3_ART_MAX_TASKS_PER_SESSION", "1"))
    _token()
    # Do not retry POST: a timeout can mean the paid task was accepted.
    with _submission_lock:
        if not 1 <= max_tasks <= 100 or _submitted >= max_tasks:
            raise RuntimeError("per-process paid task limit reached")
        _submitted += 1
    data = _api("POST", f"/api/v1/comfyui/comfyui_workflow/{workflow_id}", body=body)
    task_id = _task_id(data.get("task_id"))
    return {"task_id": task_id, "workflow_id": workflow_id, "status": data.get("status"),
            "estimated_cny": estimate["estimated_cny"],
            "cost_notice": "Estimate, not a billing cap; check the AutoDL Art ledger."}


def status(task_id: str) -> dict:
    task_id = _task_id(task_id)
    data = _api("GET", f"/api/v1/comfyui/comfyui_workflow/result/{task_id}")
    results = data.get("results") or []
    videos = [r for r in results if isinstance(r, dict) and r.get("type") == "video"]
    return {"task_id": task_id, "status": data.get("status"), "video_count": len(videos),
            "processing_seconds": data.get("duration")}


def _public_https(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("result URL must be public HTTPS")
    if parsed.port not in (None, 443):
        raise ValueError("result URL must use HTTPS port 443")
    if parsed.hostname in TRUSTED_OUTPUT_HOSTS:
        return
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("result URL hostname cannot be resolved") from exc
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError("result URL must resolve only to public addresses")


def download(task_id: str) -> dict:
    task_id = _task_id(task_id)
    data = _api("GET", f"/api/v1/comfyui/comfyui_workflow/result/{task_id}")
    if str(data.get("status", "")).upper() not in ("SUCCESS", "COMPLETED"):
        raise ValueError("task is not complete")
    videos = [r for r in data.get("results", []) if isinstance(r, dict) and r.get("type") == "video"]
    if not videos or not isinstance(videos[0].get("url"), str):
        raise ValueError("completed task has no video URL")
    url = videos[0]["url"]
    _public_https(url)
    output_dir = Path(os.getenv("H3_OUTPUT_DIR", str(Path.cwd() / "outputs"))).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"art-{task_id}.mp4"
    if target.exists():
        return {"task_id": task_id, "path": str(target), "bytes": target.stat().st_size, "already_downloaded": True}
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{task_id}-", suffix=".part", dir=output_dir, delete=False) as file:
            temporary = Path(file.name)
            try:
                with httpx.Client(timeout=120, follow_redirects=False) as client:
                    with client.stream("GET", url) as response:
                        if response.is_redirect:
                            raise RuntimeError("result URL redirected; download stopped")
                        response.raise_for_status()
                        size = 0
                        for chunk in response.iter_bytes():
                            size += len(chunk)
                            if size > 500_000_000:
                                raise RuntimeError("video exceeds 500 MB safety limit")
                            file.write(chunk)
            except httpx.HTTPError:
                raise RuntimeError("video download failed") from None
        if size == 0:
            raise RuntimeError("downloaded video is empty")
        temporary.replace(target)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return {"task_id": task_id, "path": str(target), "bytes": target.stat().st_size}
