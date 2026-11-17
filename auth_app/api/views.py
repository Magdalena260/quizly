from rest_framework import generics, permissions, status
from rest_framework.response import Response

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