
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from quiz_app.models import Quiz, Question
from quiz_app.services import (
    QuizDownloadUnavailable,
    QuizGenerationUnavailable,
    validate_quiz_data,
)


VIDEO_URL = "https://www.youtube.com/watch?v=ecbnUUTkoNk"


def create_sample_quiz(owner):
    """Create a quiz with one sample question."""
    quiz = Quiz.objects.create(
        owner=owner,
        title="Tolkien Quiz",
        description="A quiz about Middle-earth",
        video_url=VIDEO_URL,
    )
    Question.objects.create(
        quiz=quiz, question_title="Who carries the ring?",
        question_options=["Frodo", "Gandalf", "Aragorn", "Legolas"],
        answer="Frodo",
    )
    return quiz


def build_question(number):
    """Build one valid question for testing."""
    return {
        "question_title": f"Question {number}",
        "question_options": ["A", "B", "C", "D"],
        "answer": "A",
    }


def build_quiz_data():
    """Return valid quiz data containing ten questions."""
    questions = [build_question(n) for n in range(1, 11)]
    return {
        "title": "New Quiz",
        "description": "Automatically generated",
        "questions": questions,
    }


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"]
)
class QuizAPITests(APITestCase):
    """Test quiz endpoints, permissions, and validation."""

    def setUp(self):
        """Create test users and authenticate the owner."""
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            "testuser", password="SecureTestPassword123!"
        )
        self.other_user = user_model.objects.create_user(
            "otheruser", password="SecureTestPassword456!"
        )
        self.quiz = create_sample_quiz(self.user)
        self.list_url = "/api/quizzes/"
        self.detail_url = f"/api/quizzes/{self.quiz.id}/"
        self.client.force_authenticate(user=self.user)

    def post_video(self):
        """Send an authenticated quiz creation request."""
        return self.client.post(
            self.list_url,
            {"url": VIDEO_URL},
            format="json",
        )

    def test_list_own_quizzes(self):
        """Users can list their own quizzes."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_quiz_detail(self):
        """Owners can retrieve quizzes and their questions."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 1)

    def test_patch_own_quiz(self):
        """Owners can update their quiz descriptions."""
        response = self.client.patch(
            self.detail_url,
            {"description": "Updated description"},
            format="json",
        )
        self.quiz.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.quiz.description, "Updated description")

    def test_other_user_cannot_patch(self):
        """Other users cannot modify a quiz."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.detail_url,
            {"title": "Unauthorized change"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_user_cannot_delete(self):
        """Other users cannot delete a quiz."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(Quiz.objects.filter(pk=self.quiz.pk).exists())

    def test_delete_own_quiz(self):
        """Owners can delete their quizzes."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(Quiz.objects.filter(pk=self.quiz.pk).exists())

    def test_quiz_not_found(self):
        """Unknown quiz IDs return HTTP 404."""
        response = self.client.get("/api/quizzes/999999/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_access(self):
        """Anonymous users cannot access the quiz list."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_other_user_does_not_see_quiz(self):
        """Users only see quizzes they own."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_quiz(self):
        """Quiz creation saves exactly ten questions."""
        with patch(
            "quiz_app.api.views.generate_quiz_from_video",
            return_value=build_quiz_data(),
        ):
            response = self.post_video()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Quiz.objects.count(), 2)
        self.assertEqual(len(response.data["questions"]), 10)

    def test_gemini_unavailable(self):
        """Gemini failures return HTTP 503."""
        with patch(
            "quiz_app.api.views.generate_quiz_from_video",
            side_effect=QuizGenerationUnavailable("Test"),
        ):
            response = self.post_video()
        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(Quiz.objects.count(), 1)

    def test_youtube_download_unavailable(self):
        """YouTube download failures return HTTP 502."""
        with patch(
            "quiz_app.api.views.generate_quiz_from_video",
            side_effect=QuizDownloadUnavailable("Download blocked"),
        ):
            response = self.post_video()
        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertIn("detail", response.data)

    def test_create_without_url(self):
        """Quiz creation requires a URL."""
        response = self.client.post(
            self.list_url,
            {},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_reject_quiz_with_nine_questions(self):
        """Quiz validation requires exactly ten questions."""
        quiz_data = build_quiz_data()
        quiz_data["questions"].pop()
        with self.assertRaises(QuizGenerationUnavailable):
            validate_quiz_data(quiz_data)

    def test_reject_invalid_correct_answer(self):
        """Correct answers must match an available option."""
        quiz_data = build_quiz_data()
        quiz_data["questions"][0]["answer"] = "Invalid option"
        with self.assertRaises(QuizGenerationUnavailable):
            validate_quiz_data(quiz_data)

    def test_reject_non_youtube_url(self):
        """Reject quiz creation from non-YouTube websites."""
        response = self.client.post(
            self.list_url,
            {"url": "https://www.google.com"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
