from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.hashers import make_password
import hashlib
from django import forms


class CustomAdminPasswordChangeForm(AdminPasswordChangeForm):
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        return sha256_hash

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password2:
            password2 = hashlib.sha256(password2.encode()).hexdigest()
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.user.password = make_password(password)
        if commit:
            self.user.save()
        return self.user
