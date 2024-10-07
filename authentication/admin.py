from django.contrib import admin
from authentication.models import UserProfile, LoginCounter
from authentication.AdminSite.ClientAdmin import client_admin_site


# Register your models here.
class UserProfileInline(admin.StackedInline):  # Inline admin for the UserProfile
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "user"]


class LoginCounterAdmin(admin.ModelAdmin):
    list_display = ["login_counter", "user", "needs_password_change"]
    list_filter = ("user",)
    search_fields = ("user",)


admin.site.register(UserProfile, UserProfileAdmin),
admin.site.register(LoginCounter, LoginCounterAdmin),
client_admin_site.register(UserProfile, UserProfileAdmin),
