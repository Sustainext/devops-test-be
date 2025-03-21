from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup
from apps.supplier_assessment.utils.snowflake import generate_snowflake_id


class StakeHolder(AbstractModel, HistoricalModelMixin):
    id = models.PositiveBigIntegerField(
        primary_key=True, default=generate_snowflake_id, editable=False
    )
    name = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey(
        StakeHolderGroup, on_delete=models.CASCADE, related_name="stake_holder"
    )
    email = models.EmailField(max_length=500, db_index=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    poc = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name + " - " + self.group.name

    class Meta:
        ordering = ["-created_at"]
