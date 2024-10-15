from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from django.db import models
from analysis.models.Social.Gender import Gender
from common.enums.Social import AGE_GROUP_CHOICES


EMPLOYMENT_TYPE_CHOICES = [
    ("permanent employee", "Permanent Employee"),
    ("temporary employee", "Temporary Employee"),
    ("non-guaranteed-employee", "Non-guaranteed Employee"),
    ("full-time employee", "Full-time Employee"),
    ("part-time employee", "Part-time Employee"),
]


class GeneralTotalEmployees(AbstractModel, AbstractAnalysisModel):
    employment_type = models.CharField(max_length=255, choices=EMPLOYMENT_TYPE_CHOICES)
    age_group = models.CharField(max_length=255, choices=AGE_GROUP_CHOICES)
    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
        related_name="total_employees_gender",
    )
    value = models.IntegerField()
    index = models.IntegerField()

    def __str__(self):
        return self.employment_type
