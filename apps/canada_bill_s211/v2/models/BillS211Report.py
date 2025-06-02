from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from django.db import models

class BillS211Report(AbstractModel, HistoricalModelMixin):
    report = models.ForeignKey('sustainapp.Report', on_delete=models.CASCADE, related_name="canada_bill_s211_v2_report")
    screen = models.IntegerField()
    data = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['report', 'screen'], name='unique_report_screen')
        ]

    def __str__(self):
        return f"Report {self.report.id} - Screen {self.screen}"
