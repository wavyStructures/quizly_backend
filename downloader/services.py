import os
import tempfile
import subprocess


def convert_to_mp3(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + ".mp3"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ac", "1",
        "-ab", "128k",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0 or not os.path.exists(output_path):
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg conversion failed: {stderr}")

    return output_path


def download_youtube_audio(url: str) -> tuple[str, str]:
    try:
        import yt_dlp
    except ImportError as exc:
        raise ImportError(
            "yt-dlp is not installed. Install it to use YouTube download features."
        ) from exc

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "js_runtime": ["node"],
        "remote_components": "ejs:github",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "YouTube Audio")

    downloaded_file = None
    for f in os.listdir(temp_dir):
        if f.lower().endswith((".webm", ".opus", ".m4a", ".mp3")):
            downloaded_file = os.path.join(temp_dir, f)
            break

    if not downloaded_file:
        raise RuntimeError("No downloaded audio file found.")

    mp3_path = convert_to_mp3(downloaded_file)
    return mp3_path, title