from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class StakeholderEngagement(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="stakeholder_engagement"
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return super().__str__()
