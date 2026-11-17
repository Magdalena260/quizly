from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Allow access only to the quiz owner."""

    def has_object_permission(self, request, view, obj):
        """Check whether the quiz belongs to the user."""
        return obj.owner_id == request.user.id