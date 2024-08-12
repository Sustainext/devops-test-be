from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Organization, Corporateentity, Location

CATEGORY_CHOICES = [
    ("covered_by_system", "Covered by the system"),
    ("internally_audited", "Internally audited"),
    ("externally_audited", "Audited or certified by an external party"),
]


class EmployeeWorkerData(AbstractModel):

    month = models.IntegerField()
    year = models.IntegerField()
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(Corporateentity, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    number_of_employees = models.IntegerField()
    number_of_workers_not_employees = models.IntegerField()
    total_number_of_employees = models.IntegerField()

    def __str__(self):
        return self.get_category_display()

    class Meta:
        verbose_name_plural = "Employee and Worker Data"
