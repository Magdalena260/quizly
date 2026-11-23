
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz
from quiz_app.services import (
    QuizDownloadUnavailable,
    QuizGenerationUnavailable,
    generate_quiz_from_video,
)

from .permissions import IsQuizOwner
from .serializers import QuizSerializer
from .utils import save_generated_quiz, validate_video_url


class QuizListView(generics.ListCreateAPIView):
    """List personal quizzes and create new quizzes."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return quizzes belonging to the current user."""
        return (
            Quiz.objects.filter(owner=self.request.user)
            .prefetch_related("questions")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        """Generate and save a quiz from a YouTube URL."""
        url = validate_video_url(request.data.get("url"))
        try:
            quiz_data = generate_quiz_from_video(url)
        except QuizDownloadUnavailable:
            return self.download_error_response()
        except QuizGenerationUnavailable:
            return self.generation_error_response()
        quiz = save_generated_quiz(request.user, url, quiz_data)
        return Response(
            QuizSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )

    def download_error_response(self):
        """Return a response when video downloading fails."""
        return Response(
            {
                "detail": (
                    "The YouTube video could not be downloaded. "
                    "Please try again later."
                )
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    def generation_error_response(self):
        """Return a response when quiz generation fails."""
        return Response(
            {
                "detail": (
                    "Quiz generation is currently unavailable. "
                    "Please try again later."
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an individual quiz."""

    queryset = Quiz.objects.prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]

    http_method_names = [
        "get",
        "patch",
        "delete",
        "head",
        "options",
    ]
