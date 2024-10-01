from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class AboutTheReport(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="about_the_report"
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "About The Report"
        verbose_name_plural = "About The Report"

    def __str__(self):
        return f"{self.report.name} - About The Report"
