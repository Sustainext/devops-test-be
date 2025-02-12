from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Organization, Corporateentity


class StakeHolderGroup(AbstractModel, HistoricalModelMixin):
    name = models.CharField(max_length=255, db_index=True)
    group_type = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="stake_holder_group"
    )
    corporate_entity = models.ManyToManyField(
        Corporateentity, blank=True, default=None, related_name="stake_holder_group"
    )
    created_by = models.ForeignKey(
        "authentication.CustomUser",
        on_delete=models.CASCADE,
        related_name="stake_holder_groups",
    )

    def __str__(self):
        return self.name + " - " + self.group_type

    class Meta:
        unique_together = ["name", "organization", "created_by"]
