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
from sustainapp.models import Location, Corporateentity, Organization
from authentication.AdminForm.CustomUserCreationForm import CustomUserCreationForm
from django import forms


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
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = [
        "username",
        "email",
        "work_email",
        "roles",
        "client",
        "custom_role",
        "is_staff",
    ]
    list_filter = ("client", "roles")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Fields",
            {
                "fields": (
                    "custom_role",
                    "is_client_admin",
                    "admin",
                    "work_email",
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
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "client",
                    "username",
                    "first_name",
                    "last_name",
                    "job_title",
                    "department",
                    "admin",
                    "is_client_admin",
                    "password1",
                    "password2",
                    "custom_role",
                    "collect",
                    "analyse",
                    "report",
                    "track",
                    "optimise",
                    "orgs",
                    "corps",
                    "locs",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only auto-set fields when adding a new user
            obj.email = obj.username
            obj.work_email = obj.username
            default_password = "asdfghjkl@1234567890"
            obj.set_password(default_password)
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Editing an existing user
            # Pre-select linked orgs, corps, and locs
            form.base_fields["orgs"].initial = [o.id for o in obj.orgs.all()]
            form.base_fields["corps"].initial = [c.id for c in obj.corps.all()]
            form.base_fields["locs"].initial = [l.id for l in obj.locs.all()]
            # Add data-selected attributes to the fields if using templates
            form.base_fields["orgs"].widget.attrs["data-selected"] = ",".join(
                str(o.id) for o in obj.orgs.all()
            )
            form.base_fields["corps"].widget.attrs["data-selected"] = ",".join(
                str(c.id) for c in obj.corps.all()
            )
            form.base_fields["locs"].widget.attrs["data-selected"] = ",".join(
                str(l.id) for l in obj.locs.all()
            )
        if not obj:  # Only modify the form when adding a new user
            kwargs["form"] = self.add_form
        return form

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "orgs":
            client_id = request.POST.get("client") or request.GET.get("client")
            if client_id:
                kwargs["queryset"] = Organization.objects.filter(client_id=client_id)
            else:
                kwargs["queryset"] = Organization.objects.none()  # No client selected
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            kwargs["initial"] = Client.get_default_client()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",
            "authentication/js/filter_orgs.js",
            "authentication/js/password_autofill.js",
            "authentication/js/auto_set_custom_role.js",
        )


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
