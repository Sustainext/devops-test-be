# django.db.models.signals.post_save
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from django.conf import settings
import random
import string
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from sustainapp.models import ClientTaskDashboard, MyGoalOrganization
from django.contrib.auth.models import update_last_login
import hashlib
from authentication.models import (
    LoginCounter,
    UserProfile,
    CustomUser,
    UserEmailVerification,
)
import logging
from authentication.Views.VerifyEmail import generate_verification_token
import os
from sustainapp.celery_tasks.send_mail import async_send_email
from django.forms.models import model_to_dict
from django.db.models.signals import m2m_changed
from sustainapp.Cache_delete.Location_cache_delete import clear_user_location_cache
from django.utils import timezone

user_log = logging.getLogger("user_logger")
celery_logger = logging.getLogger("celery_logger")


# Signals to send Activation mail
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        user_profile_exists = hasattr(instance, "user_profile")
        token = generate_verification_token(instance)
        backend_url = os.environ.get("BACKEND_URL")
        verification_url = f"{backend_url}api/auth/verify_email/{token}/"
        # Generate a random password
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Set the generated password for the user
        instance.set_password(hashed_password)
        instance.old_password = hashed_password
        instance.save()

        username = instance.username
        first_name = instance.first_name.capitalize()
        subject = "Welcome to Sustainext! Activate your account"
        template_name = "sustainapp/email_notify_test.html"
        # Render HTML content from a template
        context = {
            "username": username,
            "first_name": first_name,
            "password": password,
            "EMAIL_REDIRECT": settings.EMAIL_REDIRECT,
            "verification_url": verification_url,
        }
        recipient_list = [instance.email]
        # recipient_list = ['utsav.pipersaniya@sustainext.ai']    #<-- For testing

        async_send_email.delay(subject, template_name, recipient_list, context)
        UserEmailVerification.objects.create(
            user=instance, token=token, sent_at=timezone.now()
        )
        celery_logger.info(f"Email sent to {instance.email} for welcome email.")
        LoginCounter.objects.create(user=instance).save()
        if not user_profile_exists:
            UserProfile.objects.create(user=instance).save()


def send_account_activation_email(user):
    first_name = user.first_name.capitalize()
    """Send an email notifying the user that their password has been changed."""
    subject = "Your Sustainext Account Is Now Activated!"
    template_name = "sustainapp/account_activation.html"
    context = {
        "first_name": first_name,
        "EMAIL_REDIRECT": settings.EMAIL_REDIRECT,
    }
    to_email = user.email
    async_send_email.delay(subject, template_name, to_email, context)
    celery_logger.info(f"Email sent to {user.email} for account activation.")


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
        recipient_email = [instance.assigned_to.email]

        if created and instance.roles != 3:
            subject = "New Emission Task Assigned"
            template_name = "sustainapp/task_assigned.html"
            context = {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "deadline": instance.deadline,
                "assigned_by": instance.assigned_by.first_name.capitalize(),
                "location": instance.location.name,
                "category": instance.category,
                "subcategory": instance.subcategory,
                "scope": instance.scope,
                "month": instance.month,
                "year": instance.year,
            }
            async_send_email.delay(subject, template_name, recipient_email, context)
            celery_logger.info(
                f"Email sent to {instance.assigned_to.email} for task assignment."
            )

        elif (
            original_task_status is not None
            and original_task_status != instance.task_status
            and instance.task_status == "approved"
        ):
            subject = "Emission Task Approved"
            approved_template = "sustainapp/task_approved.html"
            context = {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
            }
            async_send_email.delay(subject, approved_template, recipient_email, context)
            celery_logger.info(
                f"Email sent to {instance.assigned_to.email} for task approval."
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
        recipient_list = [instance.assigned_to.email]

        subject = "New Emission Task Assigned to You"
        template_name = "sustainapp/task_assigned.html"
        context = {
            "first_name": first_name,
            "task_name": task_name,
            "platform_link": platform_link,
            "deadline": instance.deadline,
            "assigned_by": instance.assigned_by.first_name.capitalize(),
            "location": instance.location.name,
            "category": instance.category,
            "subcategory": instance.subcategory,
            "scope": instance.scope,
            "month": instance.month,
            "year": instance.year,
        }
        async_send_email.delay(subject, template_name, recipient_list, context)
        celery_logger.info(
            f"Email sent to {instance.assigned_to.email} for task assignment."
        )


@receiver(task_status_changed)
def send_task_update_email(sender, instance, comments, **kwargs):
    cache_key_assigned_to = f"original_assigned_to_{instance.pk}"
    cache_key_task_status = f"original_task_status_{instance.pk}"
    original_task_status = cache.get(cache_key_task_status)
    original_assigned_to = cache.get(cache_key_assigned_to)

    if instance.assigned_to:
        first_name = instance.assigned_to.first_name.capitalize()
        task_name = instance.task_name
        platform_link = settings.EMAIL_REDIRECT
        recipient_list = [instance.assigned_to.email]

        if (
            original_task_status == "under_review"
            and instance.task_status == "in_progress"
            and original_assigned_to
        ):
            subject = "Emission Task Re-Assigned"
            template_name = "sustainapp/task_re_assigned.html"
            context = {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "deadline": instance.deadline,
                "comments": comments,  # Include comments in the context directly from Payload
                "assigned_by": instance.assigned_by.first_name.capitalize(),
                "location": instance.location.name,
                "category": instance.category,
                "subcategory": instance.subcategory,
                "scope": instance.scope,
                "month": instance.month,
                "year": instance.year,
            }
            async_send_email.delay(subject, template_name, recipient_list, context)
            celery_logger.info(
                f"Email sent to {instance.assigned_to.email} for task reassignment."
            )

        elif (
            original_task_status is not None
            and original_task_status != instance.task_status
            and instance.task_status == "reject"
        ):
            subject = "Emission Task Rejected"
            template_name = "sustainapp/task_rejected.html"
            context = {
                "first_name": first_name,
                "task_name": task_name,
                "platform_link": platform_link,
                "comments": comments,  # Include comments in the context directly from Payload
            }
            async_send_email.delay(subject, template_name, recipient_list, context)
            celery_logger.info(
                f"Email sent to {instance.assigned_to.email} for task rejection."
            )
        else:
            logging.info(f"No email conditions met for Task ID {instance.pk}")

        # Clean up cache to prevent stale data
        cache.delete(cache_key_assigned_to)
        cache.delete(cache_key_task_status)


def send_account_locked_email(user):
    first_name = user.first_name.capitalize()
    """Send an email notifying the user that their account is locked."""
    subject = "Your Sustainext Account is Locked – Reset Your Password"
    template_name = "sustainapp/account_locked.html"
    context = (
        {
            "first_name": first_name,
            "forgot_password_url": f"{settings.EMAIL_REDIRECT}/forgot-password",
        },
    )
    recipient_list = user.email
    async_send_email.delay(subject, template_name, recipient_list, context)


@receiver(post_save, sender=MyGoalOrganization)
def send_goal_notification(sender, instance, created, **kwargs):
    # Get all users linked to the organization
    organization_users = CustomUser.objects.filter(orgs=instance.organization)
    organization_name = instance.organization.name

    # Define subject and email template based on creation or update
    if created:
        subject = f"A New Goal Has Been Set for {instance.organization.name}"
        email_template = "sustainapp/goals/goals_created.html"
        # Send email to all users in the organization
        instance_data = model_to_dict(instance)
        for user in organization_users:
            email_context = {
                "first_name": user.first_name.capitalize(),
                "goal": instance_data,
                "organization_name": organization_name,
            }
            async_send_email.delay(subject, email_template, user.email, email_context)
            celery_logger.info(
                f"Email sent to {user.email} for goal creation notification."
            )
    else:
        # Retrieve the latest historical record before the update
        history_records = MyGoalOrganization.history.filter(id=instance.id).order_by(
            "-history_date"
        )

        if history_records.count() >= 2:
            last_history = history_records[1]  # Get second most recent
        else:
            last_history = None  # No previous history available

        if last_history:
            # Identify changed fields
            changed_fields = {}
            for field in instance._meta.fields:
                field_name = field.name
                if (
                    field_name == "status"
                    or field_name == "updated_at"
                    or field_name == "created_at"
                    or field_name == "created_by"
                ):
                    continue  # Ignore above field changes

                old_value = getattr(last_history, field_name, None)
                new_value = getattr(instance, field_name, None)

                if old_value != new_value:
                    changed_fields[field_name] = {"old": old_value, "new": new_value}

            # If no relevant fields were changed, do not send an email
            if not changed_fields:
                return
            instance_data = model_to_dict(instance)
            subject = f"Update on the Goal for {instance.organization.name}"
            email_template = "sustainapp/goals/goals_updated.html"

            # Email for updated goal with specific changes
            for user in organization_users:
                email_context = {
                    "first_name": user.first_name.capitalize(),
                    "goal": instance_data,
                    "changed_fields": changed_fields,
                    "organization_name": organization_name,
                }

                async_send_email.delay(
                    subject, email_template, user.email, email_context
                )
                celery_logger.info(f"Email sent to {user.email} for goal update.")


@receiver(m2m_changed, sender=CustomUser.locs.through)
def clear_cache_on_user_location_change(sender, instance, action, **kwargs):
    """
    Clears the cached location list for a user when their locations (locs) are updated.
    Runs asynchronously using Celery.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        clear_user_location_cache.delay(instance.id)
