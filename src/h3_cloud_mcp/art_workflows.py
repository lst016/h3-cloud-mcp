"""Observed AutoDL Art H3 workflow schemas and rates (2026-10-26).

These are platform page snapshots, not live prices or proof of successful paid runs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowSpec:
    workflow_id: str
    category: str
    rates: dict[str, tuple[float, float]]  # peak, offpeak CNY per output second
    resolutions: dict[str, str]  # user alias -> provider enum value
    max_seconds: int = 15
    min_images: int = 0
    max_images: int = 0
    min_audios: int = 0
    max_audios: int = 0
    first_last: bool = False
    prompt_required: bool = True
    audio_duration: bool = False
    mode: bool = False
    seed: bool = True
    prompt_limit: int = 20000


def _plain(tiers: tuple[str, ...], *, square: bool = True) -> dict[str, str]:
    values = {}
    for tier in tiers:
        for suffix in ("横", "竖"):
            value = f"{tier}{suffix}"
            values[value] = value
        if square:
            value = f"{tier}(1:1)"
            values[value] = value
    return values


def _high(large_768: bool = True) -> dict[str, str]:
    height_768 = "1376" if large_768 else "1344"
    return {
        "480p横": "480p横(864*480)",
        "480p竖": "480p竖(480*864)",
        "768p横": f"768p横({height_768}*768)",
        "768p竖": f"768p竖(768*{height_768})",
        "1088p横": "1088p横(1920*1088)",
        "1088p竖": "1088p竖(1088*1920)",
        "1440p横": "1440p横(2560*1440)",
        "1440p竖": "1440p竖(1440*2560)",
    }


LOW = {"480p": (0.04, 0.03), "768p": (0.05, 0.04)}
LOW_1080 = {**LOW, "1080p": (0.10, 0.06)}
LOW_1080_V2 = {**LOW, "1080p": (0.11, 0.07)}
ONLY_736 = {"736p": (0.06, 0.04)}
HIGH_Z = {"480p": (0.05, 0.04), "768p": (0.08, 0.06),
          "1088p": (0.08, 0.06), "1440p": (0.09, 0.07)}
HIGH_QUALITY = {**LOW, "1088p": (0.06, 0.05), "1440p": (0.07, 0.06)}
HIGH_NO_SUBTITLE = {"480p": (0.05, 0.04), "768p": (0.06, 0.05),
                    "1088p": (0.07, 0.06), "1440p": (0.08, 0.07)}


WORKFLOWS: dict[str, WorkflowSpec] = {
    "minimax_h3_lightx2v_no_pic": WorkflowSpec(
        "minimax_h3_lightx2v_no_pic", "文生", LOW, _plain(("480p", "768p"))),
    "minimax_h3_lightx2v": WorkflowSpec(
        "minimax_h3_lightx2v", "首尾帧", LOW, _plain(("480p", "768p")), first_last=True),
    "minimax_h3_lightx2v_v5": WorkflowSpec(
        "minimax_h3_lightx2v_v5", "多图参考", LOW_1080,
        _plain(("480p", "768p", "1080p")), max_seconds=10, min_images=1, max_images=9),
    "minimax_h3_lightx2v_v5_15s": WorkflowSpec(
        "minimax_h3_lightx2v_v5_15s", "多图参考", LOW,
        _plain(("480p", "768p")), min_images=1, max_images=9),
    "minimax_h3_image_audio_to_video": WorkflowSpec(
        "minimax_h3_image_audio_to_video", "图音同步", LOW_1080,
        _plain(("480p", "768p", "1080p"), square=False), min_images=1, max_images=1,
        min_audios=1, max_audios=1, prompt_required=False, audio_duration=True, seed=False),
    "minimax_h3_image_audio_to_video_v2": WorkflowSpec(
        "minimax_h3_image_audio_to_video_v2", "多图多音频", LOW_1080_V2,
        _plain(("480p", "768p", "1080p"), square=False), max_seconds=10,
        max_images=9, max_audios=3, prompt_limit=20000),
    "minimax_h3_image_audio_to_video_v2_15s": WorkflowSpec(
        "minimax_h3_image_audio_to_video_v2_15s", "多图多音频", LOW,
        _plain(("480p", "768p"), square=False), max_images=9, max_audios=3,
        prompt_limit=20000),
    "minimax_h3_b99_001": WorkflowSpec(
        "minimax_h3_b99_001", "文生", ONLY_736, _plain(("736p",))),
    "minimax_h3_b99_002": WorkflowSpec(
        "minimax_h3_b99_002", "首尾帧", ONLY_736, _plain(("736p",)), first_last=True),
    "minimax_h3_b99_003_12s": WorkflowSpec(
        "minimax_h3_b99_003_12s", "多图参考", ONLY_736, _plain(("736p",)),
        max_seconds=12, min_images=1, max_images=9, prompt_limit=20000),
    "minimax_h3_z0901": WorkflowSpec(
        "minimax_h3_z0901", "文生高画质", HIGH_Z, _high(large_768=False), prompt_limit=20000),
    "minimax_h3_z0902": WorkflowSpec(
        "minimax_h3_z0902", "六图参考", HIGH_Z, _high(), min_images=1,
        max_images=6, prompt_limit=20000),
    "minimax_h3_z0903": WorkflowSpec(
        "minimax_h3_z0903", "六图三音频", HIGH_Z, _high(), min_images=1,
        max_images=6, min_audios=1, max_audios=3, prompt_limit=20000),
    "minimax_h3_zm_u08": WorkflowSpec(
        "minimax_h3_zm_u08", "多图多音频高速", LOW, _plain(("480p", "768p")),
        min_images=1, max_images=9, max_audios=3, prompt_limit=20000),
    "minimax_h3_zm_u24": WorkflowSpec(
        "minimax_h3_zm_u24", "多图多音频升级画质", LOW, _plain(("480p", "768p")),
        min_images=1, max_images=9, max_audios=3, prompt_limit=20000),
    "minimax_h3_801": WorkflowSpec(
        "minimax_h3_801", "九图无字幕", HIGH_NO_SUBTITLE, _high(),
        min_images=1, max_images=9, mode=True, prompt_limit=20000),
    "minimax_h3_802": WorkflowSpec(
        "minimax_h3_802", "九图画质增强", HIGH_QUALITY, _high(),
        min_images=1, max_images=9, mode=True, prompt_limit=20000),
    "minimax_h3_803": WorkflowSpec(
        "minimax_h3_803", "九图三音画质增强", HIGH_QUALITY, _high(),
        min_images=1, max_images=9, max_audios=3, mode=True, prompt_limit=20000),
}


def get_workflow(workflow_id: str) -> WorkflowSpec:
    try:
        return WORKFLOWS[workflow_id]
    except KeyError as exc:
        raise ValueError("workflow_id must be one of the 18 reviewed AutoDL Art H3 workflows") from exc


def resolution_for(spec: WorkflowSpec, resolution: str | None) -> tuple[str, str]:
    if resolution is None:
        resolution = next(iter(spec.resolutions))
    if resolution in spec.resolutions:
        return resolution, spec.resolutions[resolution]
    for alias, provider_value in spec.resolutions.items():
        if resolution == provider_value:
            return alias, provider_value
    raise ValueError(f"resolution for {spec.workflow_id} must be one of: {', '.join(spec.resolutions)}")


def catalog() -> list[dict]:
    return [{"workflow_id": s.workflow_id, "category": s.category,
             "resolutions": list(s.resolutions), "max_seconds": s.max_seconds,
             "images": {"min": s.min_images, "max": s.max_images},
             "audios": {"min": s.min_audios, "max": s.max_audios},
             "first_last": s.first_last, "mode": s.mode,
             "paid_run_verified": s.workflow_id == "minimax_h3_lightx2v_no_pic"}
            for s in WORKFLOWS.values()]
