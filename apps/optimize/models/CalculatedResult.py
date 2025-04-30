# apps/optimize/models/CalculatedResult.py

from django.db import models
from apps.optimize.models import Scenerio
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin


class CalculatedResult(AbstractModel, HistoricalModelMixin):
    scenario = models.ForeignKey(
        Scenerio, on_delete=models.CASCADE, related_name="calculated_results"
    )
    year = models.PositiveIntegerField()
    activity_name = models.CharField(max_length=255)
    activity_id = models.CharField(max_length=255)
    metric = models.CharField(max_length=100)
    result = models.JSONField()

    class Meta:
        # unique_together = ("scenario", "year", "activity_id", "metric")
        indexes = [
            models.Index(fields=["scenario", "year"]),
            models.Index(fields=["activity_id"]),
        ]

    def __str__(self):
        return (
            f"{self.scenario.name} - {self.year} - {self.activity_name} - {self.metric}"
        )
