import re
from urllib.parse import parse_qs, urlsplit

import yt_dlp


def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https"):
        return None
    if parsed.hostname == "youtu.be":
        return parsed.path.strip("/")
    if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [""])[0]
        if parsed.path.startswith(("/shorts/", "/live/")):
            return parsed.path.split("/")[2]
    return None


def normalize_youtube_url(url):
    """Return a standardized YouTube video URL."""
    video_id = extract_video_id(url)

    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Invalid YouTube URL.")

    return f"https://www.youtube.com/watch?v={video_id}"


def download_audio(url, output_path):
    """Download the audio from a YouTube video."""
    url = normalize_youtube_url(url)

    options = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.download([url])