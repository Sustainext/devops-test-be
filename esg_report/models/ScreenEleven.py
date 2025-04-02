from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class ScreenEleven(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_eleven"
    )
    company_economic_performance_statement = models.JSONField(null=True, blank=True)
    financial_assistance_from_government = models.JSONField(null=True, blank=True)
    introduction_to_economic_value_creation = models.JSONField(null=True, blank=True)
    infrastructure_investement = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.report} - Screen Eleven"
