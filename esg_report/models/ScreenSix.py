from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class StakeholderEngagement(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="stakeholder_engagement"
    )
    description = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return super().__str__()