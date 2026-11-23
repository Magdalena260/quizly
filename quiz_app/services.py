
import json
import os
import tempfile
from pathlib import Path

import whisper
import yt_dlp

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from yt_dlp.utils import DownloadError


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class QuizGenerationUnavailable(Exception):
    """Raised when quiz generation fails."""


class QuizDownloadUnavailable(Exception):
    """Raised when a YouTube video cannot be downloaded."""


def get_download_options(output_path):
    """Return the yt-dlp audio download configuration."""
    return {
        "format": "bestaudio/best",
        "outtmpl": str(Path(output_path) / "audio.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "noplaylist": True,
    }


def download_audio(url, output_path):
    """Download a YouTube video's audio as MP3."""
    options = get_download_options(output_path)
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])
    except DownloadError as exc:
        raise QuizDownloadUnavailable(
            "The YouTube video could not be downloaded."
        ) from exc
    return str(Path(output_path) / "audio.mp3")


def transcribe_audio(audio_path):
    """Convert spoken audio content into text."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


def build_quiz_prompt(topic):
    """Build an English prompt for ten quiz questions."""
    instructions = (
        "Create a quiz based on the following transcript. "
        "Generate exactly 10 different questions. "
        "Each question must have exactly 4 answer options. "
        "Each question must have exactly one correct answer. "
        "The answer must exactly match one of the options. "
        "Return only valid JSON using the specified structure."
    )
    structure = get_quiz_json_structure()
    return f"{instructions}\n\n{structure}\n\nTranscript:\n{topic}"


def get_quiz_json_structure():
    """Return the expected JSON example for Gemini."""
    return json.dumps({
        "title": "Quiz title",
        "description": "Short quiz description",
        "questions": [{
            "question_title": "Question",
            "question_options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "answer": "Option A",
        }],
    })


def request_quiz_from_gemini(prompt):
    """Request structured quiz data from Gemini."""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)
    except (ServerError, ValueError, TypeError) as exc:
        raise QuizGenerationUnavailable(
            "Gemini could not generate a valid quiz."
        ) from exc


def validate_question_options(options):
    """Check that a question has four unique options."""
    if not isinstance(options, list) or len(options) != 4:
        return False
    if not all(
        isinstance(option, str) and option.strip()
        for option in options
    ):
        return False
    return len(set(options)) == 4


def validate_quiz_question(question):
    """Check the structure of one quiz question."""
    if not isinstance(question, dict):
        return False
    title = question.get("question_title")
    options = question.get("question_options")
    answer = question.get("answer")
    return (
        isinstance(title, str)
        and bool(title.strip())
        and validate_question_options(options)
        and isinstance(answer, str)
        and answer in options
    )


def validate_quiz_metadata(quiz_data):
    """Validate the quiz title and description."""
    if not isinstance(quiz_data, dict):
        raise QuizGenerationUnavailable("Invalid quiz structure.")
    for field in ("title", "description"):
        value = quiz_data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise QuizGenerationUnavailable("Invalid quiz metadata.")


def validate_quiz_data(quiz_data):
    """Ensure that Gemini returned a complete quiz."""
    validate_quiz_metadata(quiz_data)
    questions = quiz_data.get("questions")
    if not isinstance(questions, list) or len(questions) != 10:
        raise QuizGenerationUnavailable(
            "Exactly 10 questions required."
        )
    if not all(validate_quiz_question(q) for q in questions):
        raise QuizGenerationUnavailable("Invalid quiz questions.")
    return quiz_data


def generate_quiz_questions(topic):
    """Generate and validate ten quiz questions."""
    prompt = build_quiz_prompt(topic)
    quiz_data = request_quiz_from_gemini(prompt)
    return validate_quiz_data(quiz_data)


def generate_quiz_from_video(url):
    """Generate quiz data from a YouTube video."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = download_audio(url, temp_dir)
        transcript = transcribe_audio(audio_path)
        return generate_quiz_questions(transcript)
