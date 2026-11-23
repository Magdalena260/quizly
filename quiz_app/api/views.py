
from django.db import transaction

from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz, Question
from quiz_app.services import (
    QuizDownloadUnavailable,
    QuizGenerationUnavailable,
    generate_quiz_from_video,
)

from .permissions import IsQuizOwner
from .serializers import QuizSerializer


class QuizListView(generics.ListCreateAPIView):
    """List the user's quizzes or create one from a video."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the user's quizzes ordered by creation date."""
        return Quiz.objects.filter(
            owner=self.request.user
        ).prefetch_related("questions").order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """Generate and save a quiz from a YouTube URL."""
        url = request.data.get("url")

        if not isinstance(url, str) or not url.strip():
            raise serializers.ValidationError({
                "url": "Bitte eine YouTube-URL angeben."
            })

        url = url.strip()
        serializers.URLField().run_validation(url)

        try:
            quiz_data = generate_quiz_from_video(url)

        except QuizDownloadUnavailable:
            return Response(
                {
                    "detail": (
                        "The YouTube video could not be downloaded. "
                        "Please try again later."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except QuizGenerationUnavailable:
            return Response(
                {
                    "detail": (
                        "Die KI ist momentan nicht verfügbar. "
                        "Bitte versuche es später erneut."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        with transaction.atomic():
            quiz = Quiz.objects.create(
                owner=request.user,
                title=quiz_data["title"],
                description=quiz_data["description"],
                video_url=url,
            )

            Question.objects.bulk_create([
                Question(quiz=quiz, **question)
                for question in quiz_data["questions"]
            ])

        quiz.refresh_from_db()

        return Response(
            QuizSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an individual quiz."""

    queryset = Quiz.objects.prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    http_method_names = [
        "get", "patch", "delete", "head", "options"
    ]
