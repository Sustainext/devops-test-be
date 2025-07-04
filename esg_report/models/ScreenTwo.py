from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from django.db import models
from sustainapp.models import Report


class AboutTheCompanyAndOperations(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="about_the_company_and_operations",
    )
    about_the_company = models.JSONField(null=True, blank=True)
    business_relations = models.JSONField(null=True, blank=True)
    entities_included = models.JSONField(null=True, blank=True)
    supply_chain_description = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f"About the Company and Operations - {self.report.name}"
