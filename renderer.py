"""FFmpeg-first hook-based remix rendering pipeline for FreePoop V4."""

import os
import random
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from utils import get_ffmpeg_binary, temp_workspace


@dataclass
class RenderConfig:
    media_paths: List[str]
    url_paths: List[str] = field(default_factory=list)
    output_path: str = "freepoop_output.mp4"
    resolution: str = "1280x720"
    fps: int = 30
    seed: Optional[int] = None
    text_spam: str = ""
    effects: Dict[str, bool] = field(default_factory=dict)


def _run(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _parse_resolution(value: str) -> Tuple[int, int]:
    try:
        w, h = value.lower().split("x")
        return int(w), int(h)
    except Exception:
        return 1280, 720


def _normalize_to_mp4(src: str, dst: str, ffmpeg_bin: str, fps: int, w: int, h: int) -> None:
    _run([
        ffmpeg_bin, "-y", "-i", src,
        "-vf", "scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:black,fps=%d" % (w, h, w, h, fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        dst,
    ])


def _build_effect_filter(config: RenderConfig, rng: random.Random) -> str:
    vf = []
    af = []

    if config.effects.get("reverse"):
        vf.append("reverse")
        af.append("areverse")
    if config.effects.get("glitch"):
        vf.append("setpts='PTS+0.01*sin(N*0.7)'")
    if config.effects.get("stutter"):
        # cheap pseudo-stutter using frame duplication
        vf.append("tblend=all_mode=average,framestep=1")
    if config.effects.get("ear_rape"):
        af.append("volume=2.5")
    if config.effects.get("subtitle_spam"):
        txt = (config.text_spam or "FREE POOP CHAOS").replace("'", "")
        vf.append("drawtext=text='%s':x=rand(0\,(w-text_w)):y=rand(0\,(h-text_h)):fontsize=28:fontcolor=white:borderw=2" % txt)

    return ",".join(vf), ",".join(af)


def _process_clip(src: str, dst: str, config: RenderConfig, rng: random.Random, ffmpeg_bin: str) -> None:
    w, h = _parse_resolution(config.resolution)
    vf, af = _build_effect_filter(config, rng)
    cmd = [ffmpeg_bin, "-y", "-i", src]
    if vf:
        cmd += ["-vf", vf]
    if af:
        cmd += ["-af", af]
    cmd += [
        "-r", str(config.fps),
        "-s", "%dx%d" % (w, h),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        dst,
    ]
    _run(cmd)


def render_project(config: RenderConfig) -> str:
    ffmpeg_bin = get_ffmpeg_binary()
    if not ffmpeg_bin:
        raise RuntimeError("FFmpeg not detected in PATH. This build requires FFmpeg.")
    if not config.media_paths:
        raise ValueError("No media inputs provided.")

    rng = random.Random(config.seed)

    with temp_workspace() as workspace:
        w, h = _parse_resolution(config.resolution)
        normalized = []
        for idx, src in enumerate(config.media_paths):
            ext = os.path.splitext(src.lower())[1]
            norm = os.path.join(workspace, "norm_%03d.mp4" % idx)
            if ext in {".mp4", ".avi", ".mov", ".mkv", ".webm", ".gif", ".png", ".jpg", ".jpeg", ".bmp"}:
                _normalize_to_mp4(src, norm, ffmpeg_bin, config.fps, w, h)
                normalized.append(norm)

        if not normalized:
            raise ValueError("No valid video/image inputs for FFmpeg pipeline.")

        if config.effects.get("scramble"):
            rng.shuffle(normalized)

        processed = []
        for i, src in enumerate(normalized):
            dst = os.path.join(workspace, "proc_%03d.mp4" % i)
            _process_clip(src, dst, config, rng, ffmpeg_bin)
            processed.append(dst)
            if config.effects.get("random_cuts") and rng.random() < 0.5:
                cut = os.path.join(workspace, "cut_%03d.mp4" % i)
                _run([ffmpeg_bin, "-y", "-ss", "0", "-t", "0.5", "-i", dst, "-c", "copy", cut])
                processed.append(cut)

        concat_file = os.path.join(workspace, "concat.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            for p in processed:
                f.write("file '%s'\n" % p.replace("'", "'\\''"))

        _run([
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
            config.output_path,
        ])
        return config.output_path
