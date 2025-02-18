from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from apps.supplier_assessment.models.FormModels import Form
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup
from django.contrib.auth import get_user_model
from common.Validators.validate_future_date import validate_future_date

User = get_user_model()


class Assessment(AbstractModel, HistoricalModelMixin):
    """
    An assessment created by a client admin.
    It references a single form that includes all its questions.
    """

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    stakeholder_group = models.ManyToManyField(
        StakeHolderGroup, related_name="assessments"
    )
    due_date = models.DateField(validators=[validate_future_date])

    def __str__(self):
        return f"{self.name} - {self.created_by.username}"
