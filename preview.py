"""Preview generation for FreePoop V4."""

import os
import subprocess
import tempfile
from typing import Optional

from moviepy.editor import VideoFileClip  # type: ignore

from utils import is_ffmpeg_available


def generate_preview_frame(video_path: str, timestamp: float = 0.5, width: int = 320, height: int = 180) -> Optional[str]:
    """Render a low-res preview frame to PNG and return its path."""
    fd, out_png = tempfile.mkstemp(prefix="freepoop_preview_", suffix=".png")
    os.close(fd)

    if is_ffmpeg_available():
        cmd = [
            "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
            "-frames:v", "1", "-vf", "scale=%d:%d" % (width, height), out_png,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return out_png
        except Exception:
            pass

    # Fallback: MoviePy frame extraction
    try:
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(min(timestamp, max(0.0, clip.duration - 0.01)))
        from PIL import Image  # optional dependency for fallback write
        Image.fromarray(frame).resize((width, height)).save(out_png)
        clip.close()
        return out_png
    except Exception:
        return None
