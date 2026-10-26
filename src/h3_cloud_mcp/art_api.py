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

BASE = "https://autodl.art"
WORKFLOW = "minimax_h3_lightx2v_no_pic"
RESOLUTIONS = {"480p横", "480p竖", "480p(1:1)", "768p横", "768p竖", "768p(1:1)"}
# AutoDL Art currently returns a signed video URL on this Volcengine TOS host.
# A local proxy may map it to a synthetic 198.18.0.0/15 DNS address.
TRUSTED_OUTPUT_HOSTS = {"cg-comfyui-prod.tos-cn-beijing.volces.com"}
# Observed on the vendor's page, 2026-10-26. The service may change prices.
RATES = {"480p": {"peak": 0.04, "offpeak": 0.03}, "768p": {"peak": 0.05, "offpeak": 0.04}}
_submitted = 0
_submission_lock = threading.Lock()


def _validate(prompt: str, duration: int, resolution: str, seed: int | None) -> None:
    if not prompt or not prompt.strip() or len(prompt) > 4000:
        raise ValueError("prompt must contain 1 to 4000 characters")
    if type(duration) is not int or not 1 <= duration <= 15:
        raise ValueError("duration must be an integer between 1 and 15 seconds")
    if resolution not in RESOLUTIONS:
        raise ValueError(f"resolution must be one of: {', '.join(sorted(RESOLUTIONS))}")
    if seed is not None and (type(seed) is not int or not 0 <= seed < 2**64):
        raise ValueError("seed must be a nonnegative 64-bit integer")


def quote(duration: int = 5, resolution: str = "480p横") -> dict:
    _validate("quote", duration, resolution, None)
    tier = resolution[:4]
    hour = datetime.now(ZoneInfo("Asia/Shanghai")).hour
    window = "offpeak" if hour < 8 else "peak"
    return {
        "duration_seconds": duration,
        "resolution": resolution,
        "pricing_window_china": window,
        "estimated_cny": round(duration * RATES[tier][window], 2),
        "worst_observed_cny": round(duration * RATES[tier]["peak"], 2),
        "rate_observed_on": "2026-10-26",
        "warning": "Estimate only; verify current AutoDL Art price before paid submission.",
    }


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
    global _submitted
    _validate(prompt, duration, resolution, seed)
    estimate = quote(duration, resolution)
    if os.getenv("H3_ART_ENABLE_PAID") != "1":
        raise RuntimeError("Paid submission is disabled; set H3_ART_ENABLE_PAID=1 after checking the live price")
    limit = float(os.getenv("H3_ART_MAX_ESTIMATED_CNY", "0.25"))
    if not 0 < limit <= 50:
        raise ValueError("H3_ART_MAX_ESTIMATED_CNY must be > 0 and <= 50")
    if estimate["worst_observed_cny"] > limit:
        raise ValueError(f"observed peak-price estimate ¥{estimate['worst_observed_cny']:.2f} exceeds configured limit ¥{limit:.2f}")
    max_tasks = int(os.getenv("H3_ART_MAX_TASKS_PER_SESSION", "1"))
    _token()
    body = {"prompt": prompt, "duration": duration, "resolution": resolution}
    if seed is not None:
        body["seed"] = seed
    # Do not retry POST: a timeout can mean the paid task was accepted.
    with _submission_lock:
        if not 1 <= max_tasks <= 100 or _submitted >= max_tasks:
            raise RuntimeError("per-process paid task limit reached")
        _submitted += 1
    data = _api("POST", f"/api/v1/comfyui/comfyui_workflow/{WORKFLOW}", body=body)
    task_id = _task_id(data.get("task_id"))
    return {"task_id": task_id, "status": data.get("status"), "estimated_cny": estimate["estimated_cny"],
            "cost_notice": "Estimate, not a billing cap; check the AutoDL Art ledger."}


def status(task_id: str) -> dict:
    task_id = _task_id(task_id)
    data = _api("GET", f"/api/v1/comfyui/comfyui_workflow/result/{task_id}")
    results = data.get("results") or []
    videos = [r for r in results if isinstance(r, dict) and r.get("type") == "video"]
    return {"task_id": task_id, "status": data.get("status"), "video_count": len(videos),
            "duration_seconds": data.get("duration")}


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
