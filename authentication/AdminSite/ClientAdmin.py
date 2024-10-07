from django.contrib.admin import AdminSite


# Custom admin site for Client Admins
class ClientAdminSite(AdminSite):
    site_header = "Client Admin Portal"
    site_title = "Client Admin"
    # index_template = "authentication/client_admin/base_site.html"   <-- Future refence use this way to make custom admin site
    # index_title = "Welcome to the Client Admin Dashboard"

    def has_permission(self, request):
        # Limit access to users who are client admins
        user = request.user
        return user.is_authenticated and getattr(user, "is_client_admin", False)

    def each_context(self, request):
        user = request.user
        if user.is_authenticated and hasattr(user, "client") and user.client:
            client_name = user.client.name

            self.index_title = (
                f"Welcome to the Client Admin Dashboard for {client_name}"
            )
        else:
            self.index_title = "Welcome to the Client Admin Dashboard"

        context = super().each_context(request)
        context["index_title"] = self.index_title
        return context


client_admin_site = ClientAdminSite(name="client_admin")
