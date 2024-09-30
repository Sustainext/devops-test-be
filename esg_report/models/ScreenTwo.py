from common.models.AbstractModel import AbstractModel
from django.db import models
from sustainapp.models import Report


class AboutTheCompanyAndOperations(AbstractModel):
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="about_the_company_and_operations",
    )
    about_the_company = models.TextField()
    about_the_company_image = models.FileField(
        upload_to="esg_report/about_the_company/", blank=True, null=True
    )
    company_operations = models.TextField()
    entities_included = models.TextField()
    entities_included_image = models.FileField(
        upload_to="esg_report/entities_included/", blank=True, null=True
    )
    supply_chain_description = models.TextField()
    supply_chain_image = models.FileField(
        upload_to="esg_report/supply_chain/", blank=True, null=True
    )

    def __str__(self) -> str:
        return f"About the Company and Operations - {self.report.report_name}"
