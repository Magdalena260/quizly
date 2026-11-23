from rest_framework import serializers

from quiz_app.models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize individual quiz questions."""

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
        ]
        read_only_fields = fields


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz with its related questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
