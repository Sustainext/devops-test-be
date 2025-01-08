from django.db import models
from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel
from materiality_dashboard.models import MaterialityAssessment


class ReportAssessment(AbstractModel):
    """Model for storing assessments selected by user for a particular report"""

    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    materiality_assessment = models.ForeignKey(
        MaterialityAssessment, on_delete=models.CASCADE
    )
