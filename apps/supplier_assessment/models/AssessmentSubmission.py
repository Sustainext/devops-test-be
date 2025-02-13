# apps/supplier_assessment/models/assessment.py (continued)
from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.supplier_assessment.models.Assessment import Assessment
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.utils.snowflake import generate_snowflake_id


class AssessmentSubmission(AbstractModel, HistoricalModelMixin):
    """
    A submission record for an assessment by a stakeholder.
    Created immediately after the assessment is created.
    """

    id = models.BigIntegerField(
        primary_key=True,
        default=generate_snowflake_id,
        editable=False,
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="submissions"
    )
    stakeholder = models.ForeignKey(StakeHolder, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission for {self.assessment.name} by {self.stakeholder.name}"
