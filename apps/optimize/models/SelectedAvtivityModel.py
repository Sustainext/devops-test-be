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
    activity_change = models.BooleanField(default=False)
    percentage_change = models.JSONField(default=dict, null=True, blank=True)
    changes_in_activity = models.JSONField(default=dict, null=True, blank=True)
    calculated_results = models.JSONField(default=dict, null=True, blank=True)
