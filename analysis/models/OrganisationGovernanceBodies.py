from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.models.AbstractModel import AbstractModel
from analysis.models.Gender import Gender
from django.db import models
from common.enums.Social import AGE_GROUP_CHOICES


class OrganisationGovernanceBodies(AbstractModel, AbstractAnalysisModel):
    employee_category = models.CharField(
        max_length=500, help_text="Category of employees within the governance body"
    )
    age_group = models.CharField(max_length=255, choices=AGE_GROUP_CHOICES)
    minority_group_count = models.PositiveIntegerField(
        help_text="Number of employees in minority groups"
    )
    vulnerable_communities_count = models.PositiveIntegerField(
        help_text="Number of employees from vulnerable communities"
    )

    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
    )
    gender_value = models.IntegerField()
    age_group_value = models.IntegerField()
    index = models.IntegerField()

    def __str__(self) -> str:
        return self.employee_category
