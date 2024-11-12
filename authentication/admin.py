from django.contrib import admin
from authentication.models import (
    UserProfile,
    LoginCounter,
    CustomPermission,
    CustomRole,
    CustomUser,
    Client,
    UserSafeLock,
)
from authentication.AdminSite.ClientAdmin import client_admin_site
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"


class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")


class CustomRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    filter_horizontal = ("view_permissions",)


class LoginCounterAdmin(admin.ModelAdmin):
    list_display = ["login_counter", "user", "needs_password_change"]
    list_filter = ("user",)
    search_fields = ("user",)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "roles", "client", "custom_role", "is_staff"]
    list_filter = ("client", "roles")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Fields",
            {
                "fields": (
                    "roles",
                    "custom_role",
                    "is_client_admin",
                    "admin",
                    "client",
                    "collect",
                    "analyse",
                    "report",
                    "track",
                    "optimise",
                    "orgs",
                    "corps",
                    "locs",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Custom Fields",
            {"fields": ("roles", "custom_role", "is_client_admin", "admin", "client")},
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            kwargs["initial"] = Client.get_default_client()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "user"]


class UserSafeLockAdmin(admin.ModelAdmin):
    list_display = ["user", "is_locked", "failed_login_attempts", "locked_at"]




admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(LoginCounter, LoginCounterAdmin)
admin.site.register(CustomPermission, CustomPermissionAdmin)
admin.site.register(CustomRole, CustomRoleAdmin)
admin.site.register(CustomUser, CustomUserAdmin)  # Remove the comma here
admin.site.register(UserSafeLock, UserSafeLockAdmin)
client_admin_site.register(UserSafeLock, UserSafeLockAdmin)
