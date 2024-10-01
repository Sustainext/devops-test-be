from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from authentication.models import Client


class ClientFilterAdminMixin(admin.ModelAdmin):
    """
    A mixin to filter admin querysets by the client of the logged-in user.
    Only allows access to the data linked to the user's client.
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Check if the user is authenticated and is a client admin
        if not isinstance(request.user, AnonymousUser) and request.user.is_client_admin:
            return qs.filter(client=request.user.client)

        # Return the full queryset for superusers and anonymous users (login page access)
        return qs

    def has_module_permission(self, request):
        # Only allow authenticated users to check for admin permissions
        if isinstance(request.user, AnonymousUser):
            return False

        # Allow client admins and superusers to access the module
        return request.user.is_superuser or request.user.is_client_admin

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Check if the logged-in user is a client admin
        if request.user.is_client_admin:
            # Filter the client field to only show the client's own data
            if "client" in form.base_fields:
                form.base_fields["client"].queryset = Client.objects.filter(
                    id=request.user.client_id
                )
                form.base_fields["client"].initial = request.user.client_id
                form.base_fields["client"].disabled = True

        return form
