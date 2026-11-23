
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationAPITests(APITestCase):
    """Test registration and JWT cookie authentication."""

    def setUp(self):
        """Create a test user and API URLs."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecureTestPassword123!",
        )
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.logout_url = "/api/logout/"
        self.refresh_url = "/api/token/refresh/"
        self.quiz_url = "/api/quizzes/"

    def login(self):
        """Log in with valid credentials."""
        return self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "SecureTestPassword123!",
            },
            format="json",
        )

    def register_user(self, email, confirmed_password):
        """Register a user with the supplied credentials."""
        return self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": email,
                "password": "SecureNewPassword123!",
                "confirmed_password": confirmed_password,
            },
            format="json",
        )

    def test_registration(self):
        """A new user can register."""
        response = self.register_user(
            "new@example.com",
            "SecureNewPassword123!",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            get_user_model().objects.filter(
                username="newuser"
            ).exists()
        )

    def test_registration_password_mismatch(self):
        """Different passwords are rejected."""
        response = self.register_user(
            "new@example.com",
            "DifferentPassword123!",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duplicate_email(self):
        """An existing email cannot be registered again."""
        response = self.register_user(
            "test@example.com",
            "SecureNewPassword123!",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_success(self):
        """Valid credentials produce authentication cookies."""
        response = self.login()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(
            response.cookies["access_token"]["httponly"]
        )

    def test_login_invalid_credentials(self):
        """Invalid credentials return HTTP 401."""
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "WrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_without_cookie(self):
        """Refreshing without a token is rejected."""
        response = self.client.post(self.refresh_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_success(self):
        """A valid refresh cookie renews the access token."""
        login_response = self.login()
        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )
        response = self.client.post(self.refresh_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access_token", response.cookies)

    def test_logout_success(self):
        """Logout clears both authentication cookies."""
        login_response = self.login()
        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )
        response = self.client.post(self.logout_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(
            response.cookies["access_token"].value, ""
        )

    def test_logout_without_login(self):
        """Unauthenticated users cannot log out."""
        response = self.client.post(self.logout_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_access_token_invalid_after_logout(self):
        """A revoked access token cannot access protected data."""
        self.login()
        old_access = self.client.cookies["access_token"].value
        response = self.client.get(self.quiz_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.post(self.logout_url)
        self.client.cookies["access_token"] = old_access
        response = self.client.get(self.quiz_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_token_invalid_after_logout(self):
        """A revoked refresh token cannot be used again."""
        self.login()
        old_refresh = self.client.cookies["refresh_token"].value
        self.client.post(self.logout_url)
        self.client.cookies["refresh_token"] = old_refresh
        response = self.client.post(self.refresh_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
