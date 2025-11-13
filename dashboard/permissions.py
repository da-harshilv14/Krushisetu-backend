from rest_framework import permissions


class IsOfficerUser(permissions.BasePermission):
    """Allow access only to authenticated users with officer role."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "officer")
