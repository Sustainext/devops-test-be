from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from sustainapp.models import Location, Organization, Corporateentity
from analysis.models.Social.Gender import Gender

EMPLOYEE_CATEGORIES = [
    ("parental_leave_entitlement", "Parental Leave Entitlement"),
    ("taking_parental_leave", "Taking parental leave"),
    ("returning_to_work_post-leave", "Returning to Work Post-Leave"),
    ("retained_12_months_after_leave", "Retained 12 Months After Leave"),
]


class ParentalLeave(AbstractModel, AbstractAnalysisModel):
    value = models.IntegerField()
    gender = models.ForeignKey(
        Gender, on_delete=models.PROTECT, related_name="parental_leave_gender"
    )
    employee_category = models.CharField(max_length=255, choices=EMPLOYEE_CATEGORIES)
