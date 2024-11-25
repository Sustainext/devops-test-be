from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from authentication.models import Client, UserProfile


class ClientAdminSite(AdminSite):
    site_header = "Client Admin Portal"
    site_title = "Client Admin"

    def has_permission(self, request):
        user = request.user

        # Check if the user has the "ClientAdmin" role
        has_client_admin_role = user.is_client_admin
        if not has_client_admin_role:
            raise PermissionDenied("You do not have permission to access this portal.")

        return True

    def each_context(self, request):
        context = super().each_context(request)
        user = request.user

        if user.is_authenticated and hasattr(user, "client") and user.client:
            client_name = user.client.name
            self.index_title = (
                f"Welcome to the Client Admin Dashboard for {client_name}"
            )
        else:
            self.index_title = "Welcome to the Client Admin Dashboard"

        context["index_title"] = self.index_title
        return context


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "user"]


class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "uuid", "sub_domain", "okta_url", "okta_key")
    readonly_fields = ("name", "customer", "uuid")
    fields = ("name", "customer", "uuid", "sub_domain", "okta_url", "okta_key")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields
        return ()  # when creating a new object, no fields are readonly

    def has_add_permission(self, request):
        # Optionally, you can disable adding new clients through the admin
        return False


client_admin_site = ClientAdminSite(name="client_admin")
# client_admin_site.register(Client, ClientAdmin)
