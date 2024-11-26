from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from sustainapp.models import (
    Organization,
    Corporateentity,
    Location,
    Userorg,
)
from authentication.models import CustomUser, Client, UserSafeLock
from django.conf import settings
from django.db import transaction


@receiver(post_save, sender=CustomUser)
def assign_or_remove_permissions(sender, instance, created, **kwargs):
    """
    Signal to assign or remove permissions based on the `is_client_admin` flag.
    This runs every time a user is created or updated.
    """

    # TODO: Run signal only for client admin users and not on login calls.

    post_save.disconnect(
        assign_or_remove_permissions, sender=CustomUser
    )  # <--Terminate the signal to avoid recursion
    try:
        # Check if the user is a client admin
        if instance.is_client_admin:
            assign_client_admin_permissions(instance)
        else:
            remove_client_admin_permissions(instance)
    finally:
        post_save.connect(
            assign_or_remove_permissions, sender=CustomUser
        )  # <--Reconnect the signal


def assign_client_admin_permissions(user):
    # Check if the user is already staff
    if not user.is_staff:
        # user.is_staff = True  # Set is_staff to True because to access the admin site, is_staff must be True
        user.save()

    # Get the content type
    organization_content_type = ContentType.objects.get_for_model(Organization)
    corporate_content_type = ContentType.objects.get_for_model(Corporateentity)
    location_content_type = ContentType.objects.get_for_model(Location)
    user_content_type = ContentType.objects.get_for_model(CustomUser)
    # TODO: Add more models and permissions as needed

    # Permissions to be assigned to client admins
    permissions = Permission.objects.filter(
        content_type__in=[
            organization_content_type,
            corporate_content_type,
            location_content_type,
            user_content_type,
        ],
        codename__in=[
            "view_organization",
            "add_organization",
            "change_organization",
            "delete_organization",
            "add_corporateentity",
            "change_corporateentity",
            "delete_corporateentity",
            "view_corporateentity",
            "view_location",
            "add_location",
            "change_location",
            "delete_location",
            "add_customuser",
            "change_customuser",
            "delete_customuser",
            "view_customuser",
        ],
    )

    user.user_permissions.add(*permissions)
    user.save()


def remove_client_admin_permissions(user):
    # user.user_permissions.remove(*permissions)
    user.user_permissions.clear()
    user.save()

    # Optionally, remove the `is_staff` status if the user is no longer a client admin
    # if not user.is_superuser:  # Keep is_staff for superusers
    #     user.is_staff = False
    #     user.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_safelock(sender, instance, created, **kwargs):
    if created:
        safe_lock, _ = UserSafeLock.objects.get_or_create(user=instance)
        safe_lock.save()

        # Delay the handling of orgs until after the transaction commits
        transaction.on_commit(lambda: handle_user_orgs(instance))


def handle_user_orgs(instance):
    userorg, _ = Userorg.objects.get_or_create(user=instance, client=instance.client)
    if instance.orgs.exists():
        userorg.organization.set(instance.orgs.all())
    userorg.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_safelock(sender, instance, **kwargs):
    safe_lock, _ = UserSafeLock.objects.get_or_create(user=instance)
    safe_lock.save()
    instance.safelock.save()
