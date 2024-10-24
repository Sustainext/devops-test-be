from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class EcoOperationsAssesed(AbstractAnalysisModel, AbstractModel):
    operations_assessed = models.FloatField()
    operations = models.FloatField()

    def __str__(self) -> str:
        return self.id
