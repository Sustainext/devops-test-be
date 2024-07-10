from django.contrib import admin
from authentication.models import UserProfile


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "user"]


admin.site.register(UserProfile, UserProfileAdmin),
