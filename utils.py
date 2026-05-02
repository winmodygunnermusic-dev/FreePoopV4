"""Utility helpers for FreePoop V4."""

import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Generator, Optional

try:
    import requests
except Exception:  # optional dependency fallback
    requests = None


def is_ffmpeg_available() -> bool:
    """Check whether ffmpeg is visible in PATH."""
    return shutil.which("ffmpeg") is not None


def ensure_dir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path)


@contextmanager
def temp_workspace(prefix: str = "freepoop_") -> Generator[str, None, None]:
    """Create and cleanup a temporary directory."""
    tmp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def safe_basename(path: str) -> str:
    return os.path.basename(path or "")


def download_url_placeholder(url: str, out_dir: Optional[str] = None) -> Optional[str]:
    """Basic direct download helper (intended for extension with yt-dlp, archive fetchers, etc.)."""
    if not url:
        return None
    if requests is None:
        raise RuntimeError("requests is not installed; cannot download URL media")

    target_dir = out_dir or tempfile.gettempdir()
    ensure_dir(target_dir)
    filename = safe_basename(url.split("?")[0]) or "download.bin"
    out_path = os.path.join(target_dir, filename)

    with requests.get(url, stream=True, timeout=20) as response:
        response.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)
    return out_path
