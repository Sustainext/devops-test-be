from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from authentication.models import CustomUser, Client
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Location, Corporateentity, Organization
from django.core.validators import MaxValueValidator, MinValueValidator
from .data_types import DATA_TYPE_CHOICES
import collections
import json


class MyModel(AbstractModel):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Path(AbstractModel):
    name = models.CharField(max_length=300)
    slug = models.CharField(max_length=500)

    def __str__(self):
        return self.slug


class OrderedJSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        """Converts JSON data from the database into a Python OrderedDict."""
        if value is None:
            return value
        return self.to_python(value)

    def get_prep_value(self, value):
        """Prepares a Python object to be stored in the database as a JSON string."""
        if value is None:
            return None
        return json.dumps(value, separators=(",", ":"))

    def to_python(self, value):
        """Converts a JSON string retrieved from the database back into a Python OrderedDict."""
        if isinstance(value, str):
            try:
                return json.loads(value, object_pairs_hook=collections.OrderedDict)
            except ValueError:
                pass
        return value


    def db_type(self, connection):
        """Specifies the database column type as 'json' for PostgreSQL."""
        return "json"


class FieldGroup(AbstractModel):
    name = models.CharField(max_length=200)
    path = models.ForeignKey(
        Path, on_delete=models.CASCADE, default=None, related_name="fieldgroups"
    )
    meta_data = models.JSONField()
    ui_schema = models.JSONField()
    schema = OrderedJSONField()


class RawResponse(AbstractModel):
    data = OrderedJSONField(default=list)  # models.JSONField(default=list)
    path = models.ForeignKey(Path, on_delete=models.PROTECT)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        default=None,
        related_name="raw_responses",
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, default=None, related_name="raw_responses"
    )
    
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    corporate = models.ForeignKey(
        Corporateentity, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    locale = models.ForeignKey(
        Location, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    year = models.IntegerField(
        null=False, validators=[MinValueValidator(1999), MaxValueValidator(2100)]
    )
    month = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )


class DataMetric(AbstractModel):
    name = models.CharField(max_length=200)
    label = models.CharField(max_length=400)
    description = models.CharField(max_length=1000)
    path = models.ForeignKey(Path, on_delete=models.PROTECT)
    response_type = models.CharField(
        max_length=20, choices=DATA_TYPE_CHOICES, default="String"
    )

    def __str__(self):
        return self.name


class DataPoint(AbstractModel):
    """
    This is an OLAP table that is used for storing data points for data analysis
    """

    path = models.ForeignKey(Path, on_delete=models.PROTECT)
    raw_response = models.ForeignKey(
        RawResponse,
        on_delete=models.CASCADE,
        default=None,
        related_name="response_points",
        null=True,
    )
    response_type = models.CharField(
        max_length=20, choices=DATA_TYPE_CHOICES, default="String"
    )
    number_holder = models.FloatField(default=None, null=True)
    string_holder = models.CharField(default=None, null=True)
    json_holder = models.JSONField(default=None, null=True)
    data_metric = models.ForeignKey(
        DataMetric,
        on_delete=models.PROTECT,
        default=None,
        related_name="data_metric_points",
    )
    boolean_holder = models.BooleanField(default=True, null=True)
    index = models.IntegerField(default=0, null=False)
    value = models.JSONField(default=None, null=True)
    metric_name = models.CharField(default="Not Set", null=False)
    is_calculated = models.BooleanField(default=False, null=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, default=None, null=True
    )
    corporate = models.ForeignKey(
        Corporateentity, on_delete=models.CASCADE, default=None, null=True
    )
    locale = models.ForeignKey(
        Location, on_delete=models.CASCADE, default=None, null=True
    )
    year = models.IntegerField(
        null=False, validators=[MinValueValidator(1999), MaxValueValidator(2100)]
    )
    month = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    user_id = models.PositiveIntegerField(default=1, null=False)
    client_id = models.PositiveIntegerField(default=1, null=False)


class EmissionAnalysis(AbstractModel):
    activity_id = models.CharField(max_length=200)
    index = models.PositiveIntegerField()
    co2e_total = models.DecimalField(
        max_digits=20, decimal_places=3, null=True, blank=True
    )
    co2 = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True)
    n2o = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True)
    co2e_other = models.DecimalField(
        max_digits=20, decimal_places=3, null=True, blank=True
    )
    ch4 = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True)
    calculation_method = models.CharField(max_length=10)
    category = models.CharField(max_length=100)
    region = models.CharField(max_length=10)
    year = models.IntegerField()
    name = models.CharField(max_length=300)
    raw_response = models.ForeignKey(RawResponse, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name + str(self.id)
