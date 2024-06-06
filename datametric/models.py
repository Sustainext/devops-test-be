from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from authentication.models import CustomUser, Client
from common.models.AbstractModel import AbstractModel
from .data_types import DATA_TYPE_CHOICES


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


class FieldGroup(AbstractModel):
    name = models.CharField(max_length=200)
    path = models.ForeignKey(
        Path, on_delete=models.CASCADE, default=None, related_name="fieldgroups"
    )
    meta_data = models.JSONField()
    ui_schema = models.JSONField()
    schema = models.JSONField()


class RawResponse(AbstractModel):
    data = models.JSONField(default=list)
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
    location = models.CharField(max_length=200, null=True)
    year = models.IntegerField(null=True, default=2024)
    month = models.IntegerField(null=True, default=1)


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
    path = models.ForeignKey(Path, on_delete=models.PROTECT)
    raw_response = models.ForeignKey(
        RawResponse,
        on_delete=models.PROTECT,
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
