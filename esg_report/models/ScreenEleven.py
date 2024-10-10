from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class ScreenEleven(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_eleven"
    )
    company_economic_performance_statement = models.TextField(null=True, blank=True)
    financial_assistance_from_government = models.TextField(null=True, blank=True)
    introduction_to_economic_value_creation = models.TextField(null=True, blank=True)
    def __str__(self) -> str:
        return f"{self.report} - Screen Eleven"
