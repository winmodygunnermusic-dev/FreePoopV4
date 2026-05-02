"""Preview generation for FreePoop V4 (FFmpeg-only mode)."""

import os
import subprocess
import tempfile
from typing import Optional

from utils import get_ffmpeg_binary


def generate_preview_frame(video_path: str, timestamp: float = 0.5, width: int = 320, height: int = 180) -> Optional[str]:
    fd, out_png = tempfile.mkstemp(prefix="freepoop_preview_", suffix=".png")
    os.close(fd)

    ffmpeg_bin = get_ffmpeg_binary()
    if not ffmpeg_bin:
        return None

    cmd = [
        ffmpeg_bin, "-y", "-ss", str(timestamp), "-i", video_path,
        "-frames:v", "1", "-vf", "scale=%d:%d" % (width, height), out_png,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_png
    except Exception:
        return None
