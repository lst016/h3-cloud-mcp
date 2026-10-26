"""Build a minimal ComfyUI API graph for H3 FL2VA with generated audio."""

from __future__ import annotations

import os
import secrets


def build_t2va(prompt: str, width: int = 768, height: int = 448,
               frames: int = 124, steps: int = 20, seed: int | None = None) -> dict:
    if not prompt.strip() or len(prompt) > 6000:
        raise ValueError("prompt must contain 1–6000 characters")
    if width % 32 or height % 32 or not (256 <= width <= 1344) or not (256 <= height <= 768):
        raise ValueError("width and height must be multiples of 32 in the supported range")
    if frames not in (56, 73, 90, 107, 124, 141, 158, 175, 192, 209, 226, 243, 260, 277, 294, 311, 328, 345, 362):
        raise ValueError("frames must follow 17n+5, between 56 and 362")
    if not 1 <= steps <= 50:
        raise ValueError("steps must be between 1 and 50")
    seed = secrets.randbelow(2**53) if seed is None else seed
    if not 0 <= seed < 2**53:
        raise ValueError("seed must be a non-negative safe integer")
    model = os.getenv("H3_MODEL", "minimax_h3_fl2va_pruned_int8_convrot.safetensors")
    text_encoder = os.getenv("H3_TEXT_ENCODER", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors")
    video_vae = os.getenv("H3_VIDEO_VAE", "minimax_h3_video_vae_fp16.safetensors")
    audio_vae = os.getenv("H3_AUDIO_VAE", "minimax_h3_audio_vae_fp32.safetensors")

    def node(kind: str, **inputs: object) -> dict:
        return {"class_type": kind, "inputs": inputs}

    return {
        "1": node("UNETLoader", unet_name=model, weight_dtype="default"),
        "2": node("CLIPLoader", clip_name=text_encoder, type="minimax"),
        "3": node("VAELoader", vae_name=video_vae),
        "4": node("VAELoader", vae_name=audio_vae),
        "5": node("MiniMaxH3ImageToVideo", clip=["2", 0], vae=["3", 0], prompt=prompt,
                  width=width, height=height, length=frames),
        "6": node("KSamplerSelect", sampler_name="res_multistep"),
        "7": node("BasicScheduler", model=["1", 0], scheduler="simple", steps=steps, denoise=1.0),
        "8": node("RandomNoise", noise_seed=seed),
        "9": node("BasicGuider", model=["1", 0], conditioning=["5", 0]),
        "10": node("SamplerCustomAdvanced", noise=["8", 0], guider=["9", 0],
                   sampler=["6", 0], sigmas=["7", 0], latent_image=["5", 1]),
        "11": node("VAEDecode", samples=["10", 0], vae=["3", 0]),
        "12": node("VAEDecodeAudio", samples=["10", 0], vae=["4", 0]),
        "13": node("CreateVideo", images=["11", 0], audio=["12", 0], fps=24, bit_depth=8),
        "14": node("SaveVideo", video=["13", 0], filename_prefix="h3_cloud_mcp", format="auto", codec="auto"),
    }
