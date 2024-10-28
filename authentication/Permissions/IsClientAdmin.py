from rest_framework import permissions


class IsClientAdmin(permissions.BasePermission):
    """
    Custom permission to only allow client admin users to access the view.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated and any of the following are true:
        # - User is a superuser
        # - User has the `is_client_admin` flag set to True
        # - User belongs to the 'client admin' group
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_client_admin
                or request.user.groups.filter(name="client admin").exists()
            )
        )
