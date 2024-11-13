from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    message = "You must be a superuser to perform this action."

    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.user.is_superuser
        )
