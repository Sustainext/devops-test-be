from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow client admin users to access the view.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated and any of the following are true:
        # - User is a admin
        # - User has the `is_client_admin` flag set to True
        # - User belongs to the 'client admin' group
        user = request.user
        return (
            user
            and user.is_authenticated
            and (
                user.is_superuser  # Check if the user is a superuser
                or user.admin  # Check if the user is an admin
                or user.is_client_admin  # Check if the user has the is_client_admin flag
            )
        )
