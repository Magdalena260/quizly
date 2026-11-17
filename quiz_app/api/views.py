from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from quiz_app.models import Quiz

from .permissions import IsQuizOwner
from .serializers import QuizSerializer


class QuizListView(generics.ListAPIView):
    """Return all quizzes belonging to the current user."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the user's quizzes ordered by creation date."""
        return Quiz.objects.filter(
            owner=self.request.user
        ).prefetch_related("questions").order_by("-created_at")


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an individual quiz."""

    queryset = Quiz.objects.prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    http_method_names = ["get", "patch", "delete", "head", "options"]