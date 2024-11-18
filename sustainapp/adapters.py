# adapters.py in your app
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
from allauth.account.models import EmailAddress
from .serializers import CustomRegistrationSerializer  # Import the custom serializer


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        serializer = CustomRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_signup(request, user)
        if commit:
            user.save()

            # Disable email confirmation for the primary email address
            email = user_email(user)
            if email:
                email_address, created = EmailAddress.objects.get_or_create(
                    user=user, email=email, defaults={"verified": True}
                )
                if not created:
                    email_address.verified = True
                    email_address.save()

        return user
