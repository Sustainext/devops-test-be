from common.models.AbstractModel import AbstractModel
from django.db import models
from sustainapp.models import Report


class AboutTheCompanyAndOperations(AbstractModel):
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="about_the_company_and_operations",
    )
    about_the_company = models.TextField(null=True, blank=True)

    business_relations = models.TextField(null=True, blank=True)
    entities_included = models.TextField(null=True, blank=True)
    supply_chain_description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"About the Company and Operations - {self.report.name}"
