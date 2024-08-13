from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from sustainapp.models import Organization, Corporateentity, Location

CATEGORY_CHOICES = [
    ("covered_by_system", "Covered by the system"),
    ("internally_audited", "Internally audited"),
    ("externally_audited", "Audited or certified by an external party"),
]


class EmployeeWorkerData(AbstractModel,AbstractAnalysisModel):
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    number_of_employees = models.IntegerField()
    number_of_workers_not_employees = models.IntegerField()
    total_number_of_employees = models.IntegerField()

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = "Employee and Worker Data"
