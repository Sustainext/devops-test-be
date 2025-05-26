from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class GHGIntensity(AbstractModel, AbstractAnalysisModel):
    organization_specific_metric = models.CharField(max_length=255)
    metric_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=32, decimal_places=6)
    unit = models.CharField(max_length=255)
    types_included = models.JSONField(default=list, blank=True)
    custom_metric_type = models.CharField(max_length=255, null=True, blank=True)
    index = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.organization_specific_metric} - {self.metric_name}"
