from rest_framework.permissions import BasePermission


class HasThePeachAuthenticatedUser(BasePermission):
    message = "A valid ThePeach access token is required."

    def has_permission(self, request, view):
        return bool(getattr(request.user, "is_authenticated", False))
