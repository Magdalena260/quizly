from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.utils import get_login_user, set_auth_cookies

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
        response = Response({"detail": "Login successfully!", "user": {
            "id": user.id, "username": user.username, "email": user.email
        }})
        set_auth_cookies(response, user)
        return response