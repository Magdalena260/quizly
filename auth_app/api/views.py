
from rest_framework import generics, permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.utils import (
    delete_auth_cookies,
    get_login_user,
    revoke_session,
    set_auth_cookies,
    set_token_cookie,
)

from .authentication import CookieJWTAuthentication
from .serializers import RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    """Register a new user."""

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """Create a user and return a success response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user and set JWT cookies."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        """Log in and return user information."""
        user = get_login_user(request)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response({
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        })
        set_auth_cookies(response, user)
        return response


class TokenRefreshView(APIView):
    """Create a new access token using the refresh cookie."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        """Validate the refresh token and renew the access cookie."""
        raw_token = request.COOKIES.get("refresh_token")
        response = Response({"detail": "Token refreshed"})
        try:
            if not raw_token:
                raise TokenError("Missing refresh token")
            refresh = RefreshToken(raw_token)
            JWTAuthentication().get_user(refresh)
        except (TokenError, AuthenticationFailed):
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        set_token_cookie(
            response,
            "access_token",
            refresh.access_token,
        )
        return response


class LogoutView(APIView):
    """Revoke the session and remove authentication cookies."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Invalidate the session and delete cookies."""
        revoke_session(request.auth)
        response = Response({
            "detail": (
                "Log-Out successfully! All Tokens will be deleted. "
                "Refresh token is now invalid."
            )
        })
        delete_auth_cookies(response)
        return response
