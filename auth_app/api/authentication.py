from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate users through JWT cookies."""

    def authenticate(self, request):
        """Read and validate the access token."""
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        self.check_session(validated_token)
        return self.get_user(validated_token), validated_token

    def check_session(self, token):
        """Reject tokens belonging to revoked sessions."""
        session_id = token.get("session_id")
        if not session_id:
            raise AuthenticationFailed("Invalid session.")

        if BlacklistedToken.objects.filter(
            token__jti=session_id
        ).exists():
            raise AuthenticationFailed("Session has expired.")
