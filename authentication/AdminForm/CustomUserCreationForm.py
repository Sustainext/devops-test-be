from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from authentication.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """A custom Django user creation form that extends the built-in `UserCreationForm`.
    This form includes additional fields for a user's first name, last name, email, work email, client, admin status, and various permissions.
    The form also includes custom validation to ensure the username, email, and work email are all the same.
    When the form is saved, a default password is set for the user before the user is saved to the database because
    password field is not required to be entered by user, since it will generate classified password
    and set it on email automatically.
    """

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

        if email != work_email or username != email:
            raise forms.ValidationError(
                "Username, Email, and Work Email must be the same."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the default password
        default_password = "somerandompasswordwillbegenerated"
        user.set_password(default_password)

        if commit:
            user.save()
        return user
