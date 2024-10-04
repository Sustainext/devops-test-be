from django.db import models
from django.contrib.auth.models import (
    Group,
    AbstractUser,
    Permission,
)
from django.utils.translation import gettext_lazy as _
from common.models.AbstractModel import AbstractModel
from authentication.Managers.CustomUserManager import CustomUserManager
from uuid import uuid4


# Create your models here.
class Client(AbstractModel):
    name = models.CharField(max_length=256, unique=True)
    customer = models.BooleanField(default=False)
    uuid = models.UUIDField(unique=True, default=uuid4, editable=False)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    roles_choices = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="custom_userclient",
        null=True,
        blank=True,
    )

    # Fix for the reverse accessor clash
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions granted to each of their groups."
        ),
        related_name="userext_groups",  # Unique related_name
        related_query_name="userext",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="userext_permissions",  # Unique related_name
        related_query_name="userext",
    )
    objects = CustomUserManager()
    is_client_admin = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    roles = models.CharField(max_length=20, choices=roles_choices, default="employee")

    def __str__(self):
        return self.username


class UserProfile(AbstractModel):
    """
    Stores the user profile information
    """

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="user_profile"
    )
    designation = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )


class LoginCounter(AbstractModel):
    """
    Stores the number of times user logs in
    """

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="first_login"
    )
    login_counter = models.IntegerField(default=-1)
    needs_password_change = models.BooleanField(default=True, null=True, blank=True)
