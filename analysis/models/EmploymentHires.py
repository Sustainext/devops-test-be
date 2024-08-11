from common.models.AbstractModel import AbstractModel
from django.db import models
from sustainapp.models import Location, Organization, Corporateentity
from analysis.models.Gender import Gender

AGE_GROUP_CHOICES = [
    ("less than 30 years old", "Less than 30 years old"),
    ("30-50 years old", "30-50 years old"),
    ("greater than 50 years old", "Greater than 50 years old"),
]

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


class EmploymentHires(AbstractModel):
    month = models.IntegerField()
    year = models.IntegerField()
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(Corporateentity, on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="location"
    )
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
