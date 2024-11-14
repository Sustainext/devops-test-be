from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class GeneralCollectiveBargaining(AbstractAnalysisModel, AbstractModel):
    emp_covered_by_cb = models.FloatField()
    emp_in_org = models.FloatField()

    def __str__(self) -> str:
        return self.emp_covered_by_cb + " - " + self.emp_in_org
