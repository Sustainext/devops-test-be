from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class Compensation(AbstractAnalysisModel, AbstractModel):
    highest_paid_individual_compensation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Annual total compensation for the organization's highest-paid individual",
    )
    median_employee_compensation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Median annual total compensation for all employees excluding the highest-paid individual",
    )

    def __str__(self):
        return f"Salary Data: Highest Paid - {self.highest_paid_individual_compensation}, Median - {self.median_employee_compensation}"
