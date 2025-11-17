import os
import subprocess
from pathlib import Path
from django.conf import settings
from .models import Video


FFMPEG_BIN = "ffmpeg"  
HLS_SEG_DUR = int(getattr(settings, "HLS_SEG_DUR", 4))

RENDITIONS = [
    {"name": "480p", "scale": "854:480",  "bitrate": "800k",  "maxrate": "856k",  "bufsize": "1200k"},
    {"name": "720p", "scale": "1280:720", "bitrate": "1400k", "maxrate": "1498k", "bufsize": "2100k"},
    {"name": "1080p","scale": "1920:1080","bitrate": "3000k", "maxrate": "3210k", "bufsize": "4500k"},
]


def _run_ffmpeg(command: list[str]):
    """Run an FFmpeg command and raise error on failure."""
    
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg exited with code {process.returncode}")

    return process


def _rel_to_media(p: Path):
    """Return path relative to MEDIA_ROOT (for storing in FileFields)."""

    if not p or not p.exists():
        raise RuntimeError(f"Cannot calculate relative path, file does not exist: {p}")
    return os.path.relpath(p.as_posix(), settings.MEDIA_ROOT).replace("\\", "/")


