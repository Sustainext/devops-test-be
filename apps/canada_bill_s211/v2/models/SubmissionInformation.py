from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.canada_bill_s211.v2.models.CanadaBasicModel import CanadaBasicModel

class SubmissionInformation(AbstractModel, HistoricalModelMixin, CanadaBasicModel):
    screen = models.IntegerField()
    data = models.JSONField()

    def __str__(self) -> str:
        return f"Submission Information for Screen {self.screen}"

    class Meta:
        unique_together = ('organization', 'corporate', 'screen')
        verbose_name = "Submission Information for Canada Bill S211 2025"
        verbose_name_plural = "Submission Information for Canada Bill S211 2025"
        ordering = ['created_at']
        abstract = False
