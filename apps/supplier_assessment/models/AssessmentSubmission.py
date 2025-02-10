from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.supplier_assessment.models.Assessment import Assessment
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.utils.snowflake import generate_snowflake_id


class AssessmentSubmission(AbstractModel, HistoricalModelMixin):
    """ """

    id = models.BigIntegerField(
        primary_key=True,
        default=generate_snowflake_id,
        editable=False,
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    stakeholder = models.ForeignKey(StakeHolder, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
