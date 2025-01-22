# django.db.models.signals.post_save
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random
import string
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from sustainapp.models import ClientTaskDashboard
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import update_last_login
import hashlib
from authentication.models import LoginCounter, UserProfile
import logging

user_log = logging.getLogger("user_logger")


# Signals to send Activation mail
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        user_profile_exists = hasattr(instance, "user_profile")
        # Generate a random password
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Set the generated password for the user
        instance.set_password(hashed_password)
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
        first_name = instance.first_name.capitalize()
        subject = "Welcome to Sustainext! Activate your account"

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
        # recipient_list = ['utsav.pipersaniya@sustainext.ai']    #<-- For testing

        send_mail(subject, "", from_email, recipient_list, html_message=html_message)
        LoginCounter.objects.create(user=instance).save()
        if not user_profile_exists:
            UserProfile.objects.create(user=instance).save()


def send_account_activation_email(user):
    first_name = user.first_name.capitalize()
    """Send an email notifying the user that their password has been changed."""
    subject = "Your Sustainext Account Is Now Activated!"
    html_message = render_to_string(
        "sustainapp/account_activation.html",
        {
            "first_name": first_name,
            "EMAIL_REDIRECT": settings.EMAIL_REDIRECT,
        },
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    send_mail(
        subject,
        "",
        from_email,
        [to_email],
        html_message=html_message,
    )


@receiver(user_signed_up)
def disable_confirmation_email(sender, request, user, **kwargs):
    # Disable email confirmation (mark the email address as verified)
    user.emailaddress_set.filter(primary=True).update(verified=True)


@receiver(user_logged_in)
def update_last_login(sender, user, request, **kwargs):
    user_login_counter, _ = LoginCounter.objects.get_or_create(user=user)
    user_login_counter.login_counter += 1
    user_login_counter.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def check_password_change(sender, instance, created, **kwargs):
    if not created and instance.old_password:
        if instance.old_password != instance.password:
            instance.safelock.failed_login_attempts = 0
            instance.safelock.is_locked = False
            instance.safelock.locked_at = None
            instance.safelock.last_failed_at = None
            instance.safelock.save()

            if hasattr(instance, "first_login"):
                login_counter = instance.first_login

                if login_counter.needs_password_change:
                    login_counter.needs_password_change = False
                    login_counter.save()

                    send_account_activation_email(instance)
            instance.old_password = instance.password


task_status_changed = Signal()


@receiver(pre_save, sender=ClientTaskDashboard)
def store_original_details(sender, instance, **kwargs):
    if instance.pk:  # Check if the instance is being updated
        try:
            original_instance = ClientTaskDashboard.objects.get(pk=instance.pk)
            cache_key_assigned_to = f"original_assigned_to_{instance.pk}"
            cache_key_task_status = f"original_task_status_{instance.pk}"
            cache.set(
                cache_key_assigned_to, original_instance.assigned_to_id, timeout=120
            )
            cache.set(cache_key_task_status, original_instance.task_status, timeout=120)
        except ClientTaskDashboard.DoesNotExist:
            pass


@receiver(post_save, sender=ClientTaskDashboard)
def send_task_assigned_email(sender, instance, created, **kwargs):
    cache_key_task_status = f"original_task_status_{instance.pk}"
    cache_key_assigned_to = f"original_assigned_to_{instance.pk}"

    original_task_status = cache.get(cache_key_task_status)
    original_assigned_to = cache.get(cache_key_assigned_to)

    # Build common email variables
    if instance.assigned_to is not None:
        first_name = instance.assigned_to.first_name.capitalize()
        task_name = instance.task_name
        platform_link = settings.EMAIL_REDIRECT
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.assigned_to.email]

        if created and instance.roles != 3:
            subject = "New Emission Task Assigned"
            html_message = render_to_string(
                "sustainapp/task_assigned.html",
                {
                    "first_name": first_name,
                    "task_name": task_name,
                    "platform_link": platform_link,
                    "deadline": instance.deadline,
                    "assigned_by": instance.assigned_by.first_name.capitalize(),
                    "location": instance.location,
                    "category": instance.category,
                    "subcategory": instance.subcategory,
                    "scope": instance.scope,
                    "month": instance.month,
                    "year": instance.year,
                },
            )
            send_mail(
                subject, "", from_email, recipient_list, html_message=html_message
            )

        elif (
            original_task_status is not None
            and original_task_status != instance.task_status
            and instance.task_status == "approved"
        ):
            subject = "Emission Task Approved"
            html_message = render_to_string(
                "sustainapp/task_approved.html",
                {
                    "first_name": first_name,
                    "task_name": task_name,
                    "platform_link": platform_link,
                },
            )
            send_mail(
                subject, "", from_email, recipient_list, html_message=html_message
            )
    # Handle case where assigned_to changes from None to a user
    if (
        not created
        and original_assigned_to is None
        and instance.assigned_to is not None
    ):
        first_name = instance.assigned_to.first_name.capitalize()
        task_name = instance.task_name
        platform_link = settings.EMAIL_REDIRECT
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.assigned_to.email]

        subject = "New Emission Task Assigned to You"
        html_message = render_to_string(
            "sustainapp/task_assigned.html",
            {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "deadline": instance.deadline,
                "assigned_by": instance.assigned_by.first_name.capitalize(),
                "location": instance.location,
                "category": instance.category,
                "subcategory": instance.subcategory,
                "scope": instance.scope,
                "month": instance.month,
                "year": instance.year,
            },
        )
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)


@receiver(task_status_changed)
def send_task_update_email(sender, instance, comments, **kwargs):
    cache_key_assigned_to = f"original_assigned_to_{instance.pk}"
    cache_key_task_status = f"original_task_status_{instance.pk}"
    original_task_status = cache.get(cache_key_task_status)
    original_assigned_to = cache.get(cache_key_assigned_to)

    first_name = instance.assigned_to.first_name.capitalize()
    task_name = instance.task_name
    platform_link = settings.EMAIL_REDIRECT
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [instance.assigned_to.email]
    print(recipient_list)

    if (
        original_task_status == "under_review"
        and instance.task_status == "in_progress"
        and original_assigned_to
    ):
        print("triggered")
        subject = "Emission Task Re-Assigned"
        html_message = render_to_string(
            "sustainapp/task_re_assigned.html",
            {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "deadline": instance.deadline,
                "comments": comments,  # Include comments in the context directly from Payload
                "assigned_by": instance.assigned_by.first_name.capitalize(),
                "location": instance.location,
                "category": instance.category,
                "subcategory": instance.subcategory,
                "scope": instance.scope,
                "month": instance.month,
                "year": instance.year,
            },
        )
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)

    elif (
        original_task_status is not None
        and original_task_status != instance.task_status
        and instance.task_status == "reject"
    ):
        print("Reject email trigger", "Task status", instance.task_status)
        subject = "Emission Task Rejected"
        html_message = render_to_string(
            "sustainapp/task_rejected.html",
            {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "comments": comments,  # Include comments in the context directly from Payload
            },
        )
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)

    # Clean up cache to prevent stale data
    cache.delete(cache_key_assigned_to)
    cache.delete(cache_key_task_status)
