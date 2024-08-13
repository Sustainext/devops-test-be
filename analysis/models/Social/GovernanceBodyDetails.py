from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from django.db import models
from analysis.models.Social.Gender import Gender

TABLE_NAME_CHOICES = (
    (
        "number_of_individuals_within_the_organizations_governance_bodies",
        "Number of individuals within the organizations governance bodies",
    ),
    ("ratio_of_remuneration_of_women_to_men", "Ratio of remuneration of women to men"),
)


class GovernanceBodyDetails(AbstractAnalysisModel, AbstractModel):

    # Employee Category
    table_name = models.CharField(
        max_length=500,
        help_text="Table Name",
    )
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
