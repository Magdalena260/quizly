
import json
import os
import tempfile
from pathlib import Path

import whisper
import yt_dlp

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class QuizGenerationUnavailable(Exception):
    """Raised when the AI service is temporarily unavailable."""


def download_audio(url, output_path):
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(output_path) / "audio.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.download([url])

    return str(Path(output_path) / "audio.mp3")


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    return result["text"]


def generate_quiz_questions(topic):
    prompt = f"""
    Erstelle ein Quiz zum folgenden Inhalt:

    {topic}

    Erstelle 3 Quizfragen mit jeweils 4 Antwortmöglichkeiten.

    Verwende exakt diese JSON-Struktur:

    {{
        "title": "Quiztitel",
        "description": "Kurze Beschreibung",
        "questions": [
            {{
                "question_title": "Frage",
                "question_options": [
                    "Antwort 1",
                    "Antwort 2",
                    "Antwort 3",
                    "Antwort 4"
                ],
                "answer": "Antwort 1"
            }}
        ]
    }}

    Die richtige Antwort muss exakt einer der
    vier Antwortmöglichkeiten entsprechen.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )
    except ServerError as exc:
        raise QuizGenerationUnavailable(
            "Gemini is temporarily unavailable."
        ) from exc

    return json.loads(response.text)


def generate_quiz_from_video(url):
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = download_audio(url, temp_dir)
        transcript = transcribe_audio(audio_path)

        return generate_quiz_questions(transcript)
