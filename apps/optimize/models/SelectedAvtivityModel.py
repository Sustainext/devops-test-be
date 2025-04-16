from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from .OptimizeScenario import Scenerio


class SelectedActivity(AbstractModel, HistoricalModelMixin):
    """
    Model for storing selected activities.
    """

    scenario = models.ForeignKey(Scenerio, on_delete=models.CASCADE)
    scope = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    sub_category = models.CharField(max_length=255)
    activity_name = models.CharField(max_length=255)
    activity_id = models.CharField(max_length=255)
    factor_id = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=255)
    quantity2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    unit2 = models.CharField(max_length=255, null=True, blank=True)
    activity_change = models.BooleanField(default=False)
    percentage_change = models.JSONField(default=dict, null=True, blank=True)
    changes_in_activity = models.JSONField(default=dict, null=True, blank=True)
    calculated_results = models.JSONField(default=dict, null=True, blank=True)
