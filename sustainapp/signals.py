# django.db.models.signals.post_save
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random
import string
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth.signals import user_logged_in

# For Making reset password link.
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.html import strip_tags
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import update_last_login
from sustainapp.models import LoginCounter
from authentication.models import UserProfile
import logging
from authentication.models import CustomUser

user_log = logging.getLogger("user_logger")


# Signals to send Activation mail
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_activation_email(sender, instance, created, **kwargs):

    if created and not instance.is_superuser:
        # Generate a random password
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))

        # Set the generated password for the user
        instance.set_password(password)
        instance.save()

        # Use if need in future(

        # # Generate a password reset token
        # token_generator = PasswordResetTokenGenerator()
        # token = token_generator.make_token(instance)

        # # Encode the user's ID and token to include in the reset link
        # uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
        # reset_link = f"{'http://localhost:8000'}/password-reset/confirm/{uidb64}/{token}/"
        # )

        username = instance.username
        useremail = instance.email
        first_name = instance.first_name.capitalize()
        subject = "Account Activation"

        # Render HTML content from a template
        html_message = render_to_string(
            "sustainapp/email_notify_test.html",
            {
                "username": username,
                "first_name": first_name,
                "password": password,
                "EMAIL_REDIRECT": settings.EMAIL_REDIRECT,
            },
        )

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance]
        # recipient_list = ['utsav.pipersaniya@sustainext.ai']<-- For testing

        send_mail(subject, "", from_email, recipient_list, html_message=html_message)
        LoginCounter.objects.create(user=instance).save()
        UserProfile.objects.create(user=instance).save()


@receiver(user_signed_up)
def disable_confirmation_email(sender, request, user, **kwargs):
    # Disable email confirmation (mark the email address as verified)
    user.emailaddress_set.filter(primary=True).update(verified=True)


@receiver(user_logged_in)
def update_last_login(sender, user, request, **kwargs):
    user_login_counter, _ = LoginCounter.objects.get_or_create(user=user)
    user_login_counter.login_counter += 1
    user_login_counter.save()


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def capture_old_password(sender, instance, **kwargs):
    if instance.pk:
        old_password = CustomUser.objects.get(pk=instance.pk).password
        instance._old_password = old_password


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def check_password_change(sender, instance, created, **kwargs):
    if not created and hasattr(instance, "_old_password"):
        if instance._old_password != instance.password:  # Password has changed
            # Now we update the LoginCounter if it exists
            if hasattr(instance, "first_login"):
                login_counter = instance.first_login
                login_counter.needs_password_change = False
                login_counter.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_client_id(sender, instance, **kwargs):
    if (
        hasattr(instance, "client")
        and instance.client is not None
        and instance.client.id is not None
    ):
        UserProfile.objects.update_or_create(
            user=instance, defaults={"client_id": instance.client.id}
        )
