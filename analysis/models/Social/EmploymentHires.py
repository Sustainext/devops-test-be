from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from django.db import models
from sustainapp.models import Location, Organization, Corporateentity
from analysis.models.Social.Gender import Gender
from common.enums.Social import AGE_GROUP_CHOICES


EMPLOYMENT_TYPE_CHOICES = [
    ("permanent employee", "Permanent Employee"),
    ("temporary employee", "Temporary Employee"),
    ("non-guaranteed-employee", "Non-guaranteed Employee"),
    ("full-time employee", "Full-time Employee"),
    ("part-time employee", "Part-time Employee"),
]

EMPLOYMENT_TABLE_CHOICES = [
    ("new employee hire", "New Employee Hire"),
    ("employee turnover", "Employee Turnover"),
]


class EmploymentHires(AbstractModel, AbstractAnalysisModel):
    age_group = models.CharField(max_length=255, choices=AGE_GROUP_CHOICES)
    employment_type = models.CharField(max_length=255, choices=EMPLOYMENT_TYPE_CHOICES)
    employmee_table_name = models.CharField(
        max_length=255, choices=EMPLOYMENT_TABLE_CHOICES
    )
    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
        related_name="employment_hire_and_turnover_gender",
    )
    value = models.IntegerField()
    index = models.IntegerField()

    def __str__(self):
        return self.employmee_table_name + " " + self.employment_type
