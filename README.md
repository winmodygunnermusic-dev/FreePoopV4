# FreePoop V4 — Super Mega Deluxe

Absurdist remix engine for generating YouTube-Poop style montage videos from mixed media inputs.

## Features
- Tkinter desktop GUI (Windows 8.1 compatible target)
- Modular hook-based pipeline (`renderer.py`)
- Toggle-driven Poopisms:
  - Stutter, Scramble, Reverse
  - Ear-Rape audio boost
  - Overlay Spam, Glitch Mode, Subtitle Spam
  - Freeze Frames and Random Cuts
- Preview generation with FFmpeg + fallback strategy
- URL download placeholder for future `yt-dlp`/archive integrations
- Deterministic randomness support via optional seed in config
- Extensible points for advanced preprocessors/presets

## Install (Python 3.8)

```bash
pip install "moviepy==1.0.1" pillow requests
```

Install FFmpeg and ensure `ffmpeg` is available in PATH.

## Run

```bash
python main.py
```

## File Layout
- `main.py`: app entry point
- `gui.py`: Tkinter UI and controls
- `preview.py`: low-res preview frame rendering
- `renderer.py`: core rendering pipeline + effect hooks
- `utils.py`: helpers (temp dirs, ffmpeg detection, URL download placeholder)

## Notes
- URL import is currently list + placeholder download helper; direct streaming and extractor support is intentionally left as extension work.
- Pitch shift toggle is exposed in GUI as an optional hook, but not implemented by default to avoid heavy dependencies.


## Compatibility Mode (MoviePy 1.0.1 + FFmpeg)
- Renderer is tuned for MoviePy 1.0.1 style `write_videofile` usage.
- FFmpeg binary is detected from PATH and passed explicitly to MoviePy when exporting and previewing.
- Export uses primary `libx264` settings with a fallback `mpeg4` mode for stricter/older FFmpeg setups.
