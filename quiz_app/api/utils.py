
from urllib.parse import urlparse

from django.db import transaction
from rest_framework import serializers

from quiz_app.models import Quiz, Question


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def validate_video_url(url):
    """Validate that the URL belongs to YouTube."""
    if not isinstance(url, str) or not url.strip():
        raise serializers.ValidationError(
            {"url": "Please provide a YouTube URL."}
        )
    url = serializers.URLField().run_validation(url.strip())
    hostname = urlparse(url).hostname
    if hostname not in YOUTUBE_HOSTS:
        raise serializers.ValidationError(
            {"url": "Only YouTube URLs are allowed."}
        )
    return url


@transaction.atomic
def save_generated_quiz(owner, url, quiz_data):
    """Save a generated quiz and its questions."""
    quiz = Quiz.objects.create(
        owner=owner,
        title=quiz_data["title"],
        description=quiz_data["description"],
        video_url=url,
    )
    questions = [
        Question(quiz=quiz, **data)
        for data in quiz_data["questions"]
    ]
    Question.objects.bulk_create(questions)
    return quiz
