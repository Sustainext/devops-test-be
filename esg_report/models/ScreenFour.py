from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class SustainabilityRoadmap(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="sustainability_roadmap"
    )
    description = models.TextField(blank=True, null=True)
    file = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.report.name + " - Sustainability Roadmap"
