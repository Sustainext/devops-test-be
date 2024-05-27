from django.db import models
from django.contrib.auth.models import (
    Group,
    AbstractUser,
    Permission,
)
from django.utils.translation import gettext_lazy as _
from common.models.AbstractModel import AbstractModel
from authentication.Managers.CustomUserManager import CustomUserManager


# Create your models here.
class Client(AbstractModel):
    name = models.CharField(max_length=256, unique=True)
    customer = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):

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

    def __str__(self):
        return self.username
