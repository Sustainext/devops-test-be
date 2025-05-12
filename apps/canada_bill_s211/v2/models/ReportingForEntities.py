from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.canada_bill_s211.v2.models.CanadaBasicModel import CanadaBasicModel

class ReportingForEntities(AbstractModel, HistoricalModelMixin, CanadaBasicModel):
    screen = models.IntegerField()
    data = models.JSONField()

    def __str__(self) -> str:
        return f"Reporting for Org: {self.organization_id}, Corp: {self.corporate_id}, Year: {self.year}, Screen: {self.screen}"

    class Meta:
        ordering = ['created_at']
        abstract = False
        verbose_name = "Reporting For Entities"
        verbose_name_plural = "Reporting For Entities"
        unique_together = [['organization', 'corporate', 'year', 'screen']]
