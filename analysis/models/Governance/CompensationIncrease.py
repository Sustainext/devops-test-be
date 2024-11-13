from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class CompensationIncrease(AbstractAnalysisModel, AbstractModel):
    highest_paid_individual_percentage_increase = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Percentage increase in annual total compensation for the organization's highest-paid individual",
    )
    median_employee_percentage_increase = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Median percentage increase in annual total compensation for all employees excluding the highest-paid individual",
    )

    def __str__(self):
        return (
            f"Compensation Increase: Highest Paid - {self.highest_paid_individual_percentage_increase}%, "
            f"Median - {self.median_employee_percentage_increase}%"
        )
