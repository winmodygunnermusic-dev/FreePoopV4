"""Hook-based remix rendering pipeline for FreePoop V4."""

import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from moviepy.editor import (  # type: ignore
    AudioFileClip,
    CompositeVideoClip,
    ColorClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

from utils import is_ffmpeg_available, temp_workspace


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


# --- Hook-friendly pipeline API ---
def render_project(config: RenderConfig) -> str:
    rng = random.Random(config.seed)
    if not is_ffmpeg_available():
        raise RuntimeError("FFmpeg not detected in PATH. Install FFmpeg to render video.")

    with temp_workspace():
        clips = load_inputs(config)
        clips = apply_scramble(clips, config, rng)
        clips = apply_stutter(clips, config, rng)
        clips = apply_reverse(clips, config, rng)
        clips = apply_random_cuts(clips, config, rng)
        clips = apply_freeze_frames(clips, config, rng)
        clips = apply_audio_effects(clips, config)
        clips = apply_glitch(clips, config, rng)
        final = concatenate(clips)
        final = apply_overlays(final, config, rng)
        final = apply_subtitle_spam(final, config, rng)
        export(final, config)
        return config.output_path


def load_inputs(config: RenderConfig):
    clips = []
    for p in config.media_paths:
        ext = os.path.splitext(p.lower())[1]
        if ext in {".mp4", ".avi", ".mov", ".mkv", ".webm", ".gif"}:
            clips.append(VideoFileClip(p))
        elif ext in {".png", ".jpg", ".jpeg", ".bmp"}:
            clips.append(ImageClip(p, duration=2.0))
        elif ext in {".mp3", ".wav", ".ogg", ".m4a"}:
            audio = AudioFileClip(p)
            black_bg = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=min(6, audio.duration))
            clips.append(black_bg.set_audio(audio))
    if not clips:
        raise ValueError("No valid media clips loaded.")
    return clips


def apply_scramble(clips, config, rng):
    if config.effects.get("scramble"):
        shuffled = list(clips)
        rng.shuffle(shuffled)
        return shuffled
    return clips


def apply_stutter(clips, config, rng):
    if not config.effects.get("stutter"):
        return clips
    out = []
    for clip in clips:
        out.append(clip)
        if rng.random() < 0.6:
            out.append(clip.subclip(0, min(0.2, clip.duration)).fx(lambda c: c.loop(n=3)))
    return out


def apply_reverse(clips, config, rng):
    if not config.effects.get("reverse"):
        return clips
    return [c.fx(lambda clip: clip.time_mirror()) if rng.random() < 0.5 else c for c in clips]


def apply_random_cuts(clips, config, rng):
    if not config.effects.get("random_cuts"):
        return clips
    out = []
    for c in clips:
        if c.duration > 1.0 and rng.random() < 0.8:
            start = rng.uniform(0, max(0.0, c.duration - 0.8))
            out.append(c.subclip(start, min(c.duration, start + rng.uniform(0.25, 0.8))))
        else:
            out.append(c)
    return out


def apply_freeze_frames(clips, config, rng):
    if not config.effects.get("freeze"):
        return clips
    out = []
    for c in clips:
        out.append(c)
        if c.duration > 0.2 and rng.random() < 0.5:
            t = rng.uniform(0, c.duration - 0.1)
            out.append(c.to_ImageClip(t=t).set_duration(0.25))
    return out


def apply_audio_effects(clips, config):
    if not config.effects.get("ear_rape"):
        return clips
    out = []
    for c in clips:
        if c.audio is not None:
            c = c.volumex(2.5)
        out.append(c)
    return out


def apply_glitch(clips, config, rng):
    if not config.effects.get("glitch"):
        return clips
    out = []
    for c in clips:
        if c.duration > 0.4 and rng.random() < 0.7:
            seg = c.subclip(0, min(0.12, c.duration)).fx(lambda x: x.loop(n=4))
            out.extend([seg, c])
        else:
            out.append(c)
    return out


def concatenate(clips):
    return concatenate_videoclips(clips, method="compose")


def apply_overlays(final, config, rng):
    if not config.effects.get("overlay_spam"):
        return final
    overlays = [final]
    duration = max(1.0, final.duration)
    for _ in range(8):
        w = max(50, int(final.w * rng.uniform(0.08, 0.22)))
        h = max(30, int(final.h * rng.uniform(0.06, 0.18)))
        text = TextClip("WOW", color="yellow", fontsize=40).set_duration(0.2)
        text = text.resize((w, h)).set_start(rng.uniform(0, duration - 0.2))
        text = text.set_position((rng.randint(0, max(0, final.w - w)), rng.randint(0, max(0, final.h - h))))
        overlays.append(text)
    return CompositeVideoClip(overlays).set_duration(final.duration)


def apply_subtitle_spam(final, config, rng):
    if not config.effects.get("subtitle_spam"):
        return final
    words = (config.text_spam or "FREE POOP CHAOS").split()
    layers = [final]
    for _ in range(10):
        phrase = " ".join(rng.sample(words, k=min(len(words), rng.randint(1, max(1, len(words))))))
        t = TextClip(phrase, color="white", fontsize=34, stroke_color="black", stroke_width=2)
        t = t.set_start(rng.uniform(0, max(0.0, final.duration - 0.25))).set_duration(0.25)
        t = t.set_position(("center", rng.choice(["bottom", "center", "top"])))
        layers.append(t)
    return CompositeVideoClip(layers).set_duration(final.duration)


def export(final, config):
    w, h = [int(x) for x in config.resolution.lower().split("x")]
    final = final.resize((w, h))
    try:
        final.write_videofile(config.output_path, fps=config.fps, codec="libx264", audio_codec="aac")
    except Exception:
        final.write_videofile(config.output_path, fps=config.fps, preset="ultrafast")
