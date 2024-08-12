from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from django.db import models
from analysis.models.Gender import Gender


class GovernanceBodyDetails(AbstractAnalysisModel, AbstractModel):

    # Employee Category
    employee_category = models.CharField(
        max_length=500, help_text="Basic Salary per Employee Category"
    )

    # Gender distribution
    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
    )
    gender_count = models.PositiveIntegerField(
        help_text="Number of gender employees in minority groups"
    )
    location_of_operation = models.CharField(
        max_length=500,
        help_text="Location of operation",
    )
    index = models.PositiveIntegerField(
        help_text="Index of the data",
    )

    def total_employees(self):
        return self.male_count + self.female_count + self.non_binary_count

    def __str__(self):
        return f"{self.employee_category} - {self.location} - {self.year}"

    class Meta:
        verbose_name_plural = "Governance Body Details"
