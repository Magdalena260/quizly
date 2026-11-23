
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationAPITests(APITestCase):
    """Test registration and JWT cookie authentication."""

    def setUp(self):
        """Create a test user."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecureTestPassword123!",
        )

        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.logout_url = "/api/logout/"
        self.refresh_url = "/api/token/refresh/"

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

    def test_registration(self):
        """A new user can register."""
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "SecureNewPassword123!",
                "confirmed_password": "SecureNewPassword123!",
            },
            format="json",
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
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "SecureNewPassword123!",
                "confirmed_password": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duplicate_email(self):
        """An existing email cannot be registered again."""
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "test@example.com",
                "password": "SecureNewPassword123!",
                "confirmed_password": "SecureNewPassword123!",
            },
            format="json",
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
        """Invalid credentials return 401."""
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
        """A valid refresh cookie provides a new access token."""
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
        """An authenticated user can log out."""
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
        """An unauthenticated user cannot log out."""
        response = self.client.post(self.logout_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
