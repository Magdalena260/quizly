
from django.db import transaction
from rest_framework import serializers

from quiz_app.models import Quiz, Question


def validate_video_url(url):
    """Validate the submitted video URL."""
    if not isinstance(url, str) or not url.strip():
        raise serializers.ValidationError({
            "url": "Please provide a YouTube URL."
        })
    url = url.strip()
    serializers.URLField().run_validation(url)
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
