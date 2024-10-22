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
from django.utils.text import slugify
from sustainapp.models import Client, Userorg, Corporateentity, Location, Organization

# Create your models here.


class CustomPermission(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)  # Add the slug field

    def save(self, *args, **kwargs):
        # Automatically create the slug based on the name if it's not already set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CustomRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    view_permissions = models.ManyToManyField(CustomPermission)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_role(cls):
        return cls.objects.get_or_create(name="SystemAdmin")[0]


class CustomUser(AbstractUser):
    roles_choices = (
        ("system_admin", "System Admin"),
        ("client_admin", "Client Admin"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_DEFAULT,
        related_name="custom_userclient",
        null=True,
        blank=True,
        default=Client.get_default_client,
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
    custom_role = models.ForeignKey(
        "CustomRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=20, blank=True)
    job_title = models.CharField(_("job title"), max_length=100, blank=True)
    department = models.CharField(_("department"), max_length=100, blank=True)
    work_email = models.CharField(_("department"), max_length=200, blank=True)
    collect = models.BooleanField(default=True)
    analyse = models.BooleanField(default=True)
    report = models.BooleanField(default=False)
    optimise = models.BooleanField(default=False)
    track = models.BooleanField(default=False)
    permissions_checkbox = models.BooleanField(default=False)
    orgs = models.ManyToManyField(Organization, related_name="organizations")
    corps = models.ManyToManyField(Corporateentity, related_name="corporates")
    locs = models.ManyToManyField(Location, related_name="locations")

    @property
    def default_role(self):
        if self.custom_role is None:
            default_role, _ = CustomRole.objects.get_or_create(name="SystemAdmin")
            self.custom_role = default_role
            self.save()
        return self.custom_role

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
