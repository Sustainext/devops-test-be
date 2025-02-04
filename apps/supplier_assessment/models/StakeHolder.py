from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup


class StakeHolder(AbstractModel, HistoricalModelMixin):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        StakeHolderGroup, on_delete=models.CASCADE, related_name="stake_holder"
    )
    email = models.EmailField(max_length=500, blank=True, null=True)
    poc = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name + " - " + self.group.name
