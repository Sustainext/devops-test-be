from django.db import models
from common.models.AbstractModel import AbstractModel
from .OptimizeScenario import Scenerio
from common.models.HistoricalModel import HistoricalModelMixin


class BusinessMetric(AbstractModel, HistoricalModelMixin):
    """
    Model for storing business metrics data.
    """

    scenario = models.OneToOneField(
        Scenerio, on_delete=models.CASCADE, related_name="business_metrics"
    )
    fte = models.BooleanField(default=False)
    fte_data = models.JSONField(default=dict, null=True, blank=True)
    area = models.BooleanField(default=False)
    area_data = models.JSONField(default=dict, null=True, blank=True)
    revenue = models.BooleanField(default=False)
    revenue_data = models.JSONField(default=dict, null=True, blank=True)
    production_volume = models.BooleanField(default=False)
    production_volume_data = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"Scenario_business_metric_{self.id}"
