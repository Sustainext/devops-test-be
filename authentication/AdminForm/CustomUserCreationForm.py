from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from authentication.models import CustomUser
from sustainapp.models import Userorg


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
            user.save()  # Save the user first to ensure it has a primary key

            # Ensure the related Userorg object exists
            userorg, created = Userorg.objects.get_or_create(
                user=user, defaults={"client": user.client}
            )

            # Update the organization Many-to-Many relationship
            if "orgs" in self.cleaned_data:
                userorg.organization.set(self.cleaned_data["orgs"])
            userorg.save()

        return user
