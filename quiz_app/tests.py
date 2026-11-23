
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from quiz_app.models import Quiz, Question
from quiz_app.services import QuizGenerationUnavailable


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
class QuizAPITests(APITestCase):
    """Test quiz endpoints and permissions."""

    def setUp(self):
        """Create two users and a sample quiz."""
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="testuser",
            password="SecureTestPassword123!",
        )
        self.other_user = user_model.objects.create_user(
            username="otheruser",
            password="SecureTestPassword456!",
        )
        self.quiz = Quiz.objects.create(
            owner=self.user,
            title="Tolkien-Quiz",
            description="Ein Quiz über Mittelerde",
            video_url="https://www.youtube.com/watch?v=ecbnUUTkoNk",
        )
        Question.objects.create(
            quiz=self.quiz,
            question_title="Wer trägt den Ring?",
            question_options=[
                "Frodo", "Gandalf", "Aragorn", "Legolas"
            ],
            answer="Frodo",
        )
        self.list_url = "/api/quizzes/"
        self.detail_url = f"/api/quizzes/{self.quiz.id}/"
        self.client.force_authenticate(user=self.user)

    def test_list_own_quizzes(self):
        """A user can list their own quizzes."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_quiz_detail(self):
        """The owner can retrieve a quiz with its questions."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 1)

    def test_patch_own_quiz(self):
        """The owner can update a quiz."""
        response = self.client.patch(
            self.detail_url,
            {"description": "Aktualisierte Beschreibung"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz.refresh_from_db()
        self.assertEqual(
            self.quiz.description, "Aktualisierte Beschreibung"
        )

    def test_other_user_cannot_patch(self):
        """Another user cannot update the quiz."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.detail_url,
            {"title": "Fremder Zugriff"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_delete(self):
        """Another user cannot delete the quiz."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Quiz.objects.filter(pk=self.quiz.pk).exists())

    def test_delete_own_quiz(self):
        """The owner can delete their quiz."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(Quiz.objects.filter(pk=self.quiz.pk).exists())

    def test_quiz_not_found(self):
        """A missing quiz returns 404."""
        response = self.client.get("/api/quizzes/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """An anonymous user cannot list quizzes."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_other_user_does_not_see_quiz(self):
        """A user cannot see another user's quiz in the list."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_quiz(self):
        """A video can generate and save a quiz with questions."""
        quiz_data = {
            "title": "Neues Quiz",
            "description": "Automatisch erstellt",
            "questions": [
                {
                    "question_title": f"Frage {number}",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A",
                }
                for number in range(1, 4)
            ],
        }

        with patch(
            "quiz_app.api.views.generate_quiz_from_video",
            return_value=quiz_data,
        ):
            response = self.client.post(
                self.list_url,
                {"url": "https://www.youtube.com/watch?v=ecbnUUTkoNk"},
                format="json",
            )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(Quiz.objects.count(), 2)
        self.assertEqual(
            Question.objects.filter(
                quiz_id=response.data["id"]
            ).count(),
            3,
        )

    def test_gemini_unavailable(self):
        """A Gemini outage produces a controlled 503 response."""
        with patch(
            "quiz_app.api.views.generate_quiz_from_video",
            side_effect=QuizGenerationUnavailable("Test"),
        ):
            response = self.client.post(
                self.list_url,
                {"url": "https://www.youtube.com/watch?v=ecbnUUTkoNk"},
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(Quiz.objects.count(), 1)

    def test_create_without_url(self):
        """Creating a quiz without a URL is rejected."""
        response = self.client.post(
            self.list_url, {}, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )
