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
            "work_email",
            "client",
            "admin",
            "password1",
            "password2",
            "collect",
            "analyse",
            "report",
            "track",
            "optimise",
            "orgs",
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        work_email = cleaned_data.get("work_email")

        if username and email and work_email:
            if email != work_email or username != email:
                raise forms.ValidationError(
                    "Username, Email, and Work Email must be the same."
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the default password
        default_password = "asdfghjkl@1234567890"
        user.set_password(default_password)

        if commit:
            user.save()
        return user
