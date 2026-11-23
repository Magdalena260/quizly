from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .api.serializers import LoginSerializer


def get_login_user(request):
    """Validate credentials and authenticate the user."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return authenticate(
            request=request,
            **serializer.validated_data
        )
    return None


def set_token_cookie(response, name, token):
    """Store a JWT in an HttpOnly cookie."""
    response.set_cookie(
        key=name,
        value=str(token),
        max_age=int(token.lifetime.total_seconds()),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/",
    )


def set_auth_cookies(response, user):
    """Generate and store access and refresh tokens."""
    refresh = RefreshToken.for_user(user)
    refresh["session_id"] = refresh["jti"]
    set_token_cookie(response, "access_token", refresh.access_token)
    set_token_cookie(response, "refresh_token", refresh)


def delete_auth_cookies(response):
    """Remove authentication cookies."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


def revoke_session(token):
    """Revoke the refresh token and associated access tokens."""
    outstanding_token = OutstandingToken.objects.get(
        jti=token["session_id"]
    )
    BlacklistedToken.objects.get_or_create(
        token=outstanding_token
    )
