from django.db import models
from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin


class ScreenNine(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_nine"
    )
    statement = models.JSONField(null=True, blank=True)
    board_gov_statement = models.JSONField(null=True, blank=True)
    remuneration_policies = models.JSONField(null=True, blank=True)
    policy_not_public_reason = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.report.name} - Screen Nine Statements"
