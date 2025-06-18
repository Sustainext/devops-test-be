from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from django.core.validators import MaxValueValidator, MinValueValidator


class TCFDReport(AbstractModel, HistoricalModelMixin):
    """
    Model for storing TCFD Report data screen wise.
    """

    report = models.ForeignKey("sustainapp.Report", on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)
    screen_name = models.CharField(max_length=255)

    def __str__(self):
        return f"tcfd_{self.report.name}"
