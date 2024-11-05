from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from authentication.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "client",
            "admin",
            "password1",
            "password2",
        )
