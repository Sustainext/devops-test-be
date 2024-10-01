from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class MissionVisionValues(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="mission_vision_values"
    )
    mission = models.TextField(blank=True, null=True)
    mission_image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.report.name + " - " + self.mission
