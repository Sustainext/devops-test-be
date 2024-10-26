from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin


class StatementOfUseModel(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        "sustainapp.Report",
        on_delete=models.CASCADE,
        related_name="statement_of_uses",
    )
    statement_of_use = models.TextField()

    def __str__(self):
        return f"Statement of Use for Content Index {self.report.id}"
