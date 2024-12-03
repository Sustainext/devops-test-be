from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    Group,
)
from django.contrib.postgres.fields import ArrayField
from django.db.models import Case, Value, When, UniqueConstraint
from django.utils.translation import gettext_lazy as _
import os
from django.core.files.storage import default_storage
from django.conf import settings
from authentication.models import CustomUser, Client
import re
from common.models.AbstractModel import AbstractModel
from common.Validators.validate_future_date import validate_future_date
from sustainapp.Validators.IsPositiveInteger import validate_positive_integer
from sustainapp.Validators.LocationValidators import (
    validate_latitude,
    validate_longitude,
)
from sustainapp.Managers.ClientFiltering import ClientFiltering
from functools import cached_property
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from uuid import uuid4
from authentication.models import CustomUser, Client

# Create your models here.


def validate_non_empty(value):
    """Validator for non empty fields"""
    if len(value) == 0:
        raise ValidationError("Field Cannot be empty")


# * Preferences App
class Sdg(models.Model):
    """Add the SDG's here"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/sdg", null=True, blank=True, max_length=4098
    )
    Target_no = models.PositiveSmallIntegerField()
    goal_no = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Framework(models.Model):
    """Add the Frameworks here"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/framework", null=True, blank=True, max_length=4098
    )

    def __str__(self):
        return self.name


class Regulation(models.Model):
    """Add the Regulations here - Yash"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/regulation", null=True, blank=True, max_length=4098
    )

    def __str__(self):
        return self.name


class Certification(models.Model):
    """Add the Certifications here"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/certifcations", null=True, blank=True, max_length=4098
    )

    def __str__(self):
        return self.name


class Target(models.Model):
    """Add the Target here"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/Target", null=True, blank=True, max_length=4098
    )

    def __str__(self):
        return self.name


class Rating(models.Model):
    """Add the Rating here"""

    name = models.CharField(max_length=256)
    Image = models.ImageField(
        upload_to="images/rating", null=True, blank=True, max_length=4098
    )

    def __str__(self):
        return self.name


class Sector(models.Model):
    """this is Category"""

    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Category(models.Model):
    """This is sub-category"""

    name = models.CharField(max_length=256)
    sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, related_name="categorysector"
    )

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=256)
    contribution = models.CharField(max_length=256, null=True, blank=True)
    total_emissions = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name


class User_client(AbstractModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_userclient",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="client_userclient",
        default=Client.get_default_client,
    )

    objects = ClientFiltering()


class Organization(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="client_Org",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    type_corporate_entity = models.CharField(max_length=256, null=True, blank=True)
    owner = models.CharField(max_length=256, null=True, blank=True)
    location_of_headquarters = models.CharField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    website = models.CharField(max_length=256, null=True, blank=True)
    fax = models.CharField(max_length=256, null=True, blank=True)
    employeecount = models.CharField(max_length=256, null=True, blank=True)
    sector = models.CharField(max_length=256, null=True, blank=True)
    revenue = models.CharField(max_length=256, null=True, blank=True)
    subindustry = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    countryoperation = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    date_format = models.CharField(max_length=256, null=True, blank=True)
    currency = models.CharField(max_length=256, null=True, blank=True)
    timezone = models.CharField(max_length=256, null=True, blank=True)
    language = models.CharField(max_length=256, null=True, blank=True)
    from_date = models.CharField(max_length=256, null=True, blank=True)
    to_date = models.CharField(max_length=256, null=True, blank=True)
    sdg = models.ManyToManyField(Sdg, related_name="organisationdetailsdg", blank=True)
    rating = models.ManyToManyField(
        Rating, related_name="organisationdetailrating", blank=True
    )
    certification = models.ManyToManyField(
        Certification, related_name="organisationdetailcertification", blank=True
    )
    target = models.ManyToManyField(
        Target, related_name="organisationdetailtarget", blank=True
    )
    framework = models.ManyToManyField(
        Framework, related_name="organisationdetailframework", blank=True
    )
    regulation = models.ManyToManyField(
        Regulation, related_name="organisationdetailregulation", blank=True
    )
    active = models.BooleanField(default=False)
    no_of_employees = models.CharField(max_length=256, null=True, blank=True)
    amount = models.CharField(max_length=256, null=True, blank=True)
    ownership_and_legal_form = models.CharField(max_length=256, null=True, blank=True)
    group = models.CharField(max_length=256, null=True, blank=True)
    type_of_corporate_entity = models.CharField(max_length=256, null=True, blank=True)
    location_of_headquarters = models.CharField(max_length=256, null=True, blank=True)
    sub_industry = models.CharField(max_length=256, null=True, blank=True)
    type_of_business_activities = models.CharField(
        max_length=256, null=True, blank=True
    )
    type_of_product = models.CharField(max_length=256, null=True, blank=True)
    type_of_services = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "name"], name="unique_client_organization"
            )
        ]

    objects = ClientFiltering()


class Userorg(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="client_User_Org",
        default=Client.get_default_client,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userorg_user",
        null=True,
        blank=True,
    )
    organization = models.ManyToManyField(
        Organization, related_name="userorg_organization"
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="userorg_group",
        null=True,
        blank=True,
    )
    department = models.CharField(max_length=256, null=True, blank=True)
    designation = models.CharField(max_length=256, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="images/userorg", null=True, blank=True
    )
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return str(self.user) if self.user else "No User"

    objects = ClientFiltering()

    # def clean(self):
    #     if self.client.id and self.user.id and self.client.id != self.user.client.id:
    #         raise ValidationError("Use and client mismatch")
    #     if (
    #         self.client.id
    #         and self.organization.id
    #         and self.client.id != self.organization.client.id
    #     ):
    #         raise ValidationError("Use and client mismatch")
    #     super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


currency_choices = (
    ("USD", "US Dollars"),
    ("EUR", "Euros"),
    ("AUD", "Australian Dollars"),
    ("INR", "Indian Rupee"),
    ("GBP", "Pound Sterling"),
)
dateformat_choices = (("1", "dd/mm/yy"), ("2", "mm/dd/yy"), ("3", "yy/mm/dd"))
timezone_choices = (("1", "UTC"), ("2", "AR"), ("3", "AE"), ("4", "IL"), ("5", "AU"))


class Corporateentity(models.Model):
    legalFrom_choices = (
        ("1", "Sole Proprietorship"),
        ("2", "General Partnership"),
        ("3", "Limited Liability Company (LLC)"),
        ("4", "Corporations (C-Corp and S-Corp)"),
        ("5", "Limited Liability Partnership (LLP)"),
    )
    ownership_choices = (
        ("1", "Single Ownership"),
        ("2", "Partnership"),
        ("3", "Public Sector"),
        ("4", "Private Sector"),
        ("5", "Cooperative Organisation (Or Societies)"),
        ("6", "Joint Stock Company(Public Limited Company)"),
        ("7", "Joint Stock Company(Private Limited Company)"),
    )
    corporatetype_choices = (
        ("1", "LLP (Limited liability partnership)"),
        ("2", "ILP (Incorporated limited partnership)"),
        ("3", "Inc. (Incorporated)"),
        ("4", "Ltd. (Limited)"),
        ("5", "NL(No Liability)"),
        ("6", "Pty. Ltd. (Proprietary Limited Company)"),
        ("7", "Pty(Unlimited Proprietary)"),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="corporatenetityclient",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    corporatetype = models.CharField(max_length=256, null=True, blank=True)
    ownershipnature = models.CharField(max_length=256, null=True, blank=True)
    location_headquarters = models.CharField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    website = models.CharField(max_length=256, null=True, blank=True)
    fax = models.CharField(max_length=256, null=True, blank=True)
    employeecount = models.CharField(max_length=256, null=True, blank=True)
    revenue = models.CharField(max_length=256, null=True, blank=True)
    sector = models.CharField(max_length=256, null=True, blank=True)
    subindustry = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    Country = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    zipcode = models.CharField(max_length=256, null=True, blank=True)
    date_format = models.CharField(max_length=1000, null=True, blank=True)
    currency = models.CharField(max_length=256, null=True, blank=True)
    timezone = models.CharField(max_length=256, null=True, blank=True)
    language = models.CharField(max_length=256, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    framework = models.ForeignKey(
        Framework,
        on_delete=models.CASCADE,
        related_name="corporatenetityframework",
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="corporatenetityorg",
        null=True,
        blank=True,
    )
    legalform = models.CharField(max_length=256, null=True, blank=True)
    ownership = models.CharField(max_length=256, null=True, blank=True)
    group = models.CharField(max_length=256, null=True, blank=True)
    location_of_headquarters = models.CharField(max_length=256, null=True, blank=True)
    amount = models.CharField(max_length=256, null=True, blank=True)
    type_of_business_activities = models.CharField(
        max_length=1000, null=True, blank=True
    )
    type_of_product = models.CharField(max_length=1000, null=True, blank=True)
    type_of_services = models.CharField(max_length=1000, null=True, blank=True)
    type_of_business_relationship = models.CharField(
        max_length=1000, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"], name="unique_organization_corporate"
            )
        ]

    objects = ClientFiltering()

    def clean(self):
        if (
            self.client.id
            and self.organization.id
            and self.client.id != self.organization.client.id
        ):
            raise ValidationError(
                "Client ID and Organization ID mismatch: Organization does not belong to the specified client."
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Location(models.Model):
    is_headquarters_choices = (
        ("Non-Headquarter Location", "Non-Headquarter Location"),
        ("Headquarter  Location", "Headquarter  Location"),
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="locationclient",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    phone = models.CharField(max_length=256, null=True, blank=True)
    mobile = models.CharField(max_length=256, null=True, blank=True)
    website = models.CharField(max_length=256, null=True, blank=True)
    fax = models.CharField(max_length=256, null=True, blank=True)
    employeecount = models.CharField(max_length=256, null=True, blank=True)
    revenue = models.CharField(max_length=256, null=True, blank=True)
    sector = models.CharField(max_length=256, null=True, blank=True)
    sub_industry = models.CharField(max_length=256, null=True, blank=True)
    streetaddress = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=256)
    state = models.CharField(max_length=256)
    city = models.CharField(max_length=256, null=True, blank=True)
    zipcode = models.CharField(max_length=256, null=True, blank=True)
    dateformat = models.CharField(max_length=256, null=True, blank=True)
    currency = models.CharField(max_length=256, null=True, blank=True)
    timezone = models.CharField(max_length=256, null=True, blank=True)
    language = models.CharField(max_length=256, null=True, blank=True)
    corporateentity = models.ForeignKey(
        Corporateentity,
        on_delete=models.CASCADE,
        related_name="location",
        null=True,
        blank=True,
    )
    typelocation = models.CharField(max_length=256, null=True, blank=True)
    location_type = models.CharField(max_length=256, null=True, blank=True)
    area = models.CharField(max_length=256, null=True, blank=True)
    type_of_business_activities = models.CharField(
        max_length=256, null=True, blank=True
    )
    type_of_product = models.CharField(max_length=256, null=True, blank=True)
    type_of_services = models.CharField(max_length=256, null=True, blank=True)
    latitude = models.FloatField(validators=[validate_latitude], null=True, blank=True)
    longitude = models.FloatField(
        validators=[validate_longitude], null=True, blank=True
    )
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["corporateentity", "name"],
                name="unique_corporate_corporateentity",
            )
        ]

    objects = ClientFiltering()

    def clean(self):
        if (
            self.client.id
            and self.corporateentity.id
            and self.client.id != self.corporateentity.client.id
        ):
            raise ValidationError(
                "Client ID and Corporate ID mismatch: Corporate does not belong to the specified client."
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Contact(models.Model):
    contact_choices = (("1", "main"), ("2", "mobile"), ("3", "fax"))
    type = models.CharField(max_length=256, choices=contact_choices)
    number = models.PositiveIntegerField()
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="contact"
    )

    def __str__(self):
        return self.number


# * Manager
class BatchManager(models.Manager):
    def latest_time(self, locations):
        latest_year = (
            self.get_queryset()
            .filter(location__in=locations)
            .order_by("-year")
            .values("year")[0]["year"]
        )
        latest_year_records = self.get_queryset().filter(year=latest_year)
        month_priority = Case(
            When(month="JAN", then=Value(12)),
            When(month="FEB", then=Value(11)),
            When(month="MAR", then=Value(10)),
            When(month="APR", then=Value(9)),
            When(month="MAY", then=Value(8)),
            When(month="JUN", then=Value(7)),
            When(month="JUL", then=Value(6)),
            When(month="AUG", then=Value(5)),
            When(month="SEP", then=Value(4)),
            When(month="OCT", then=Value(3)),
            When(month="NOV", then=Value(2)),
            When(month="DEC", then=Value(1)),
        )
        latest_month = (
            latest_year_records.alias(month_priority=month_priority)
            .order_by("-year", "month_priority")
            .values("month")[0]["month"]
        )
        latest_record = latest_year_records.filter(month=latest_month)
        record = {
            "latest_year": latest_year,
            "latest_month": latest_month,
            "latest_record": latest_record,
        }
        return record


class Batch(models.Model):
    """Overall Batch nos- Each Batch record for 1 month data"""

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="batchclient",
        default=Client.get_default_client,
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="batch_location"
    )
    year = models.PositiveIntegerField()
    month = models.CharField(max_length=56, null=True, blank=True)
    total_co2e = models.DecimalField(
        max_digits=100, decimal_places=50, null=True, blank=True
    )

    objects = models.Manager()
    latest_fields = BatchManager()

    # add unique constrainsts
    class Meta:
        constraints = [
            UniqueConstraint(fields=["location", "year", "month"], name="unique_batch")
        ]

    objects = ClientFiltering()

    def clean(self):
        if (
            self.client.id
            and self.location.id
            and self.client.id != self.location.client.id
        ):
            raise ValidationError(
                "Client ID and location ID mismatch: Location does not belong to the specified client."
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Scope(models.Model):
    name = models.CharField(max_length=256)

    objects = ClientFiltering()


# TODO: To be Deleted
class RowDataBatch(models.Model):
    """For combination of scope and number is unique in each batch.Row_number to be sent from frontend .."""

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="RowDataBatchclient",
        default=Client.get_default_client,
    )
    scope = models.PositiveIntegerField(null=True, blank=True)
    row_number = models.PositiveIntegerField()
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="rowdatabatch_batch"
    )
    sector = models.CharField(max_length=1024, null=True, blank=True)
    category = models.CharField(max_length=1024, null=True, blank=True)
    value1 = models.DecimalField(max_digits=100, decimal_places=50, default=0.00)
    unit_type = models.CharField(max_length=256, null=True, blank=True)
    unit1 = models.CharField(max_length=256, null=True, blank=True)
    value2 = models.DecimalField(
        max_digits=100, decimal_places=50, default=0.00, null=True, blank=True
    )
    unit2 = models.CharField(max_length=256, null=True, blank=True)
    file = models.TextField(null=True, blank=True)
    filename = models.CharField(max_length=256, null=True, blank=True)
    assign_to = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    file_modified_at = models.CharField(max_length=256, null=True, blank=True)
    activity_id = models.CharField(max_length=1000)
    emmissionfactorid = models.CharField(max_length=1000, null=True, blank=True)
    activity_name = models.CharField(max_length=1000, null=True, blank=True)
    co2e = models.DecimalField(max_digits=100, decimal_places=50, null=True, blank=True)
    co2e_unit = models.CharField(max_length=256, null=True, blank=True)
    co2e_calculation_method = models.CharField(max_length=256, null=True, blank=True)
    co2e_calculation_origin = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    activity_id = models.CharField(max_length=512, null=True, blank=True)
    uuid = models.UUIDField(null=True, blank=True)
    access_type = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    source_dataset = models.CharField(max_length=256, null=True, blank=True)
    year = models.CharField(max_length=256, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    source_lca_activity = models.CharField(max_length=256, null=True, blank=True)
    data_quality_flags = ArrayField(
        models.CharField(max_length=256, null=True, blank=True), null=True, blank=True
    )
    constituent_gases = models.JSONField(null=True, blank=True)
    audit_trail = models.CharField(max_length=256, null=True, blank=True)
    activity_data = models.JSONField(null=True, blank=True)

    objects = ClientFiltering()

    def clean(self):
        if self.client.id and self.batch.id and self.client.id != self.batch.client.id:
            raise ValidationError(
                "Client ID and Batch ID mismatch: Batch does not belong to the specified client."
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Task(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Taskclient",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    row_data_batch = models.ForeignKey(
        RowDataBatch,
        on_delete=models.CASCADE,
        related_name="task_rowdatabatch",
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_to"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_by"
    )
    # created_by=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='task_created_by',on_delete=models.SET_NULL,null=True,blank=True)
    # updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='task_updated_by',on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.name

    objects = ClientFiltering()


class Mygoal(models.Model):
    """Creating a relation for My Goals in SustainextHQ/Dashboard"""

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Mygoalclient",
        default=Client.get_default_client,
    )
    title = models.CharField(max_length=1024)
    deadline = models.DateField(
        help_text="Enter only future dates", null=False, blank=False
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Mygoal_User"
    )
    completed = models.BooleanField(default=False)

    objects = ClientFiltering()

    def clean(self):
        if (
            self.client.id
            and self.assigned_to.id
            and self.client.id != self.assigned_to.client.id
        ):
            raise ValidationError("User does not belong to this client")
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TaskDashboard(models.Model):
    # status = assigned task ( default = Flase)  indiacating that it is his personal task, if this is true, then this is a task assigned by boss
    #
    taskname = models.CharField(max_length=1024)
    deadline = models.DateField(
        help_text="Enter only future dates", null=False, blank=False
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Task_User"
    )
    # org  = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name ="Task_User")
    # assigned_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name ="Task_User")    Boss

    completed = models.BooleanField(default=False)  # Pending or Over due, completed
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="TaskDashboard_client",
        null=True,
        blank=True,
        default=Client.get_default_client,
    )
    objects = ClientFiltering()

    def clean(self):
        if (
            self.client.id
            and self.assigned_to.id
            and self.client.id != self.assigned_to.client.id
        ):
            raise ValidationError("User does not belong to this client")
        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Bussinessrelationship(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Bussinessrelationship_client",
        default=Client.get_default_client,
    )
    partnerships = models.CharField(max_length=256)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_Bussinessrelationship",
    )
    # created_by=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='Bussinessrelationship_created_by',on_delete=models.SET_NULL,null=True,blank=True)
    # updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='Bussinessrelationship_updated_by',on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.partnerships

    objects = ClientFiltering()


class Bussinessactivity(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Bussinessactivityclient",
        default=Client.get_default_client,
    )
    activity_name = models.CharField(max_length=256)
    service = models.CharField(max_length=256)
    Products = models.CharField(max_length=256)
    markets = models.CharField(max_length=256)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_bussiness_activity",
    )
    bussinessrelationship = models.ForeignKey(
        Bussinessrelationship,
        on_delete=models.CASCADE,
        related_name="bussinessactivity",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.activity_name

    objects = ClientFiltering()


class Companyactivities(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Companyactivitiesclient",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    bussiness_relationship = models.ForeignKey(
        Bussinessrelationship,
        on_delete=models.CASCADE,
        related_name="companyactivityBussinessrelationship",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    objects = ClientFiltering()


sub_group_choices = (
    ("1", "Employees"),
    ("2", "Customer"),
    ("3", "Supplier"),
    ("4", "Regulators"),
    ("5", "Local Communities"),
    ("6", "NGO's"),
    ("7", "Investors"),
    ("8", "Trade unions"),
    ("9", "Leadership"),
    ("10", "Management"),
    ("11", "Employees"),
)


class Stakeholdergroup(models.Model):
    internal_choices = (("Internal", "Internal"), ("External", "External"))
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Stakeholdergroupclient",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=256, choices=internal_choices)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_stakeholdergroup",
        null=True,
        blank=True,
    )
    data = models.JSONField(null=True, blank=True)
    content_type = models.PositiveSmallIntegerField(null=True, blank=True)
    object_id = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    objects = ClientFiltering()


class Stakeholder(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Stakeholderclient",
        default=Client.get_default_client,
    )
    email = models.EmailField()
    name = models.CharField(max_length=256)
    phone_number = models.PositiveIntegerField(null=True, blank=True)
    stakeholdergroup = models.ForeignKey(
        Stakeholdergroup, on_delete=models.CASCADE, related_name="stakeholder"
    )
    data = models.JSONField(null=True)

    objects = ClientFiltering()


def get_upload_path(instance, filename):
    report_id = instance.pk

    env_name = os.environ.get("ENV_NAME")
    if env_name is None:
        env_name = "NoEnv"

    # Get the file extension from the original filename
    file_extension = os.path.splitext(filename)[1]

    # Construct the new filename based on the report_id and the original extension
    new_filename = f"{report_id}{file_extension}"

    return os.path.join("images", env_name, "report_logo", new_filename)


class Report(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="client_reports",
        default=Client.get_default_client,
    )
    name = models.CharField(max_length=256, null=True, blank=True)
    report_type = models.CharField(max_length=256, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    last_report = models.DateTimeField(auto_now_add=True)
    report_by = models.CharField(max_length=256, null=True, blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="report_organization",
        null=True,
        blank=True,
    )
    corporate = models.ForeignKey(
        Corporateentity,
        on_delete=models.CASCADE,
        related_name="report_corporate",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports"
    )
    org_logo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    about_the_organization = models.TextField(null=True, blank=True)
    roles_and_responsibilities = models.TextField(null=True, blank=True)
    organizational_boundries = models.TextField(null=True, blank=True)
    excluded_sources = models.TextField(null=True, blank=True)
    designation_of_organizational_admin = models.TextField(null=True, blank=True)
    reporting_period_name = models.CharField(max_length=255, null=True, blank=True)
    from_year = models.DateField(max_length=255, null=True, blank=True)
    to_year = models.DateField(max_length=255, null=True, blank=True)
    data_source = models.JSONField(null=True, blank=True)
    calender_year = models.DateField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    STATUS_CHOICES = [(0, "Deactivate"), (1, "Activate")]

    status = models.IntegerField(choices=STATUS_CHOICES)
    investment_corporates = models.JSONField(blank=True, null=True)

    def clean(self):
        if self.corporate and self.organization:
            if self.corporate.organization != self.organization:
                raise ValidationError(
                    "Corporate must be associated with the same organization."
                )
        # if self.client.id and self.user.id and self.client.id!=self.user.id:
        #     raise ValidationError("User doesnt belong to same client")

    def save(self, *args, **kwargs):
        fields_to_clean = [
            "about_the_organization",
            "roles_and_responsibilities",
            "excluded_sources",
        ]

        for field in fields_to_clean:
            original_value = getattr(self, field, None)
            if original_value:
                # Remove <h4>, <h5>, and <h6> tags
                cleaned_value = re.sub(r"</?(h4|h5|h6)[^>]*>", "", original_value)
                setattr(self, field, cleaned_value)

        self.full_clean()  # Run full validation before saving
        if self.pk:
            try:
                existing_instance = Report.objects.get(pk=self.pk)
                if existing_instance.org_logo and self.org_logo:
                    # This checks if the file has changed. It's a simple check and might need to be adapted.
                    if existing_instance.org_logo.name != self.org_logo.name:
                        # Delete the old file from Azure Blob Storage using its name, not path
                        existing_file_name = existing_instance.org_logo.name
                        if default_storage.exists(existing_file_name):
                            default_storage.delete(existing_file_name)
            except Report.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Unnamed Report {self.pk}"

    objects = ClientFiltering()


class AnalysisData2(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="AnalysisData2client",
        default=Client.get_default_client,
    )
    report_id = models.CharField(max_length=255, unique=True)
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"AnalysisData2 - Report ID: {self.report_id}"

    objects = ClientFiltering()


class ClientTaskDashboard(AbstractModel):
    task_name = models.CharField(max_length=1024)
    deadline = models.DateField(
        help_text="Enter only future dates",
        null=False,
        blank=False,
        validators=[validate_future_date],
    )
    assigned_to = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="task"
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subordinates_task",
    )
    roles = models.IntegerField(null=True, blank=True)

    STATUS_CHOICES = [
        ("in_progress", "in_progress"),
        ("approved", "approved"),
        ("under_review", "under_review"),
        ("completed", "completed"),
        ("reject", "reject"),
    ]
    task_status = models.CharField(
        max_length=64, choices=STATUS_CHOICES, default="in_progress"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, blank=True
    )
    category = models.CharField(max_length=1024, null=True, blank=True)
    subcategory = models.CharField(max_length=1024, null=True, blank=True)
    scope = models.CharField(max_length=1024, null=True, blank=True)
    month = models.CharField(max_length=1024, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    activity_id = models.CharField(max_length=2048, null=True, blank=True)
    value1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    value2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit1 = models.CharField(max_length=1024, null=True, blank=True)
    unit2 = models.CharField(max_length=1024, null=True, blank=True)
    unit_type = models.CharField(max_length=1024, null=True, blank=True)
    file_data = models.JSONField(null=True, blank=True)
    file_uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="fileuploadedby",
        null=True,
        blank=True,
    )
    activity = models.CharField(max_length=2048, null=True, blank=True)
    region = models.CharField(max_length=1024, null=True, blank=True)
    objects = ClientFiltering()


class ZohoInfo(AbstractModel):
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name="zoho_info"
    )
    iframe_url = models.URLField(max_length=2000)
    table_no = models.CharField(max_length=30, validators=[validate_positive_integer])
    table_name = models.CharField(max_length=255, unique=True)

    @cached_property
    def client_name(self):
        return self.client.name

    def __str__(self) -> str:
        return self.client_name + " " + self.table_name


class TrackDashboard(AbstractModel):
    REPORT_CHOICES = [
        ("emission", "Emission"),
        ("energy", "Energy"),
        ("waste", "Waste"),
        ("employment", "Employment"),
        ("ohs", "Occupational Health and Safety (OHS)"),
        ("diversity_inclusion", "Diversity & Inclusion"),
        ("community_development", "Community Development"),
        ("water_and_effluents", "Water & Effluents"),
        ("material", "Material"),
        ("general", "General"),
        ("economic", "Economic"),
        ("governance", "Governance"),
    ]
    table_name = models.CharField(max_length=255, default="")
    report_name = models.CharField(max_length=1024, choices=REPORT_CHOICES)
    report_id = models.CharField(max_length=255)
    group_id = models.CharField(max_length=255)


class Department(AbstractModel):
    name = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.client} - {self.name}"
