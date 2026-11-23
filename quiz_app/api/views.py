
from django.db import transaction

from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz, Question
from quiz_app.services import generate_quiz_from_video

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

        url_field = serializers.URLField()
        url_field.run_validation(url)

        quiz_data = generate_quiz_from_video(url)

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

        response_data = QuizSerializer(quiz).data

        return Response(
            response_data,
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
