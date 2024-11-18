from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class GeneralWorkersNotEmp(AbstractAnalysisModel, AbstractModel):
    type_of_worker = models.CharField(max_length=255, null=True, blank=True)
    total_workers = models.FloatField()
    contractual_relationship = models.CharField(max_length=255, null=True, blank=True)
    work_performed = models.CharField(max_length=255, null=True, blank=True)
    engagement_approach = models.CharField(max_length=255, null=True, blank=True)
    third_party = models.CharField(max_length=255, null=True, blank=True)
    index = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.type_of_worker} - {self.total_workers}"
