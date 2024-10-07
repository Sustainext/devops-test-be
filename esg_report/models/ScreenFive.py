from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Report


class AwardAndRecognition(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="award_recognition"
    )
    description = models.TextField(blank=True, null=True)
    file = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Award and Recognition for {self.report.name}"
