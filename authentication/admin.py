from django.contrib import admin, messages
from authentication.models import (
    UserProfile,
    LoginCounter,
    CustomPermission,
    CustomRole,
    CustomUser,
    Client,
    UserSafeLock,
    UserEmailVerification,
)
from authentication.AdminSite.ClientAdmin import client_admin_site
from django.contrib.auth.admin import UserAdmin
from authentication.AdminForm.CustomUserCreationForm import CustomUserCreationForm
from authentication.forms import CustomAdminPasswordChangeForm

from django.urls import path
from django.utils.html import format_html
from django.shortcuts import redirect
from django.utils import timezone
from authentication.Views.VerifyEmail import generate_verification_token
from sustainapp.celery_tasks.send_mail import async_send_email
import os
import hashlib
import random
import string
from django.conf import settings


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
    change_password_form = CustomAdminPasswordChangeForm
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
        if not change:
            obj.email = obj.username
            obj.work_email = obj.username
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            org_ids = obj.orgs.values_list("id", flat=True)
            corp_ids = obj.corps.values_list("id", flat=True)
            loc_ids = obj.locs.values_list("id", flat=True)

            form.base_fields["orgs"].initial = org_ids
            form.base_fields["corps"].initial = corp_ids
            form.base_fields["locs"].initial = loc_ids

            form.base_fields["orgs"].widget.attrs["data-selected"] = ",".join(
                map(str, org_ids)
            )
            form.base_fields["corps"].widget.attrs["data-selected"] = ",".join(
                map(str, corp_ids)
            )
            form.base_fields["locs"].widget.attrs["data-selected"] = ",".join(
                map(str, loc_ids)
            )
        else:
            kwargs["form"] = self.add_form
        return form

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
    list_display = [
        "user",
        "is_locked",
        "failed_login_attempts",
        "last_failed_at",
        "locked_at",
    ]


@admin.register(UserEmailVerification)
class UserEmailVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "activation_status",
        "sent_at",
        "resend_count",
        "last_resend_at",
        "resend_button",
    )

    def activation_status(self, obj):
        return obj.status

    def resend_button(self, obj):
        if obj.status != "verified" and obj.check_and_mark_token_expired():
            return format_html(
                '<a class="button" href="{}">Resend</a>', f"resend/{obj.pk}/"
            )
        return "-"

    resend_button.short_description = "Resend Email"
    resend_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "resend/<int:pk>/",
                self.admin_site.admin_view(self.resend_email_view),
                name="resend-verification-email",
            ),
        ]
        return custom_urls + urls

    def resend_email_view(self, request, pk):
        record = self.get_object(request, pk)
        user = record.user
        new_token = generate_verification_token(user)
        verification_url = (
            f"{os.environ.get('BACKEND_URL')}api/auth/verify_email/{new_token}/"
        )

        # Hased password and set it to user's password
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user._skip_password_change_signal = True
        user.set_password(hashed_password)
        user.old_password = hashed_password
        user.first_login.needs_password_change = True
        user.first_login.save()
        user.save()

        subject = "Welcome to Sustainext! Activate your account"
        template_name = "sustainapp/email_notify_test.html"
        context = {
            "username": user.username,
            "first_name": user.first_name.capitalize(),
            "password": password,
            "EMAIL_REDIRECT": settings.EMAIL_REDIRECT,
            "verification_url": verification_url,
        }

        try:
            async_send_email.delay(subject, template_name, [user.email], context)
            record.token = new_token
            record.sent_at = timezone.now()
            record.last_resend_at = timezone.now()
            record.resend_count += 1
            record.status = "pending"
            record.last_error = None
            record.save()
            self.message_user(request, f"Verification email resent to {user.email}")
        except Exception as e:
            record.last_error = str(e)
            record.status = "failed"
            record.save()
            self.message_user(
                request, f"Failed to resend email: {str(e)}", level=messages.ERROR
            )

        return redirect("/admin/authentication/useremailverification/")


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(LoginCounter, LoginCounterAdmin)
admin.site.register(CustomPermission, CustomPermissionAdmin)
admin.site.register(CustomRole, CustomRoleAdmin)
admin.site.register(CustomUser, CustomUserAdmin)  # Remove the comma here
admin.site.register(UserSafeLock, UserSafeLockAdmin)
client_admin_site.register(UserSafeLock, UserSafeLockAdmin)
