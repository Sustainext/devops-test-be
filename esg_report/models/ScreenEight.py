from django.db import models
from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel


class MaterialityStatement(AbstractModel):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="materiality_statement"
    )
    statement = models.TextField()

    class Meta:
        verbose_name_plural = "Materiality Statements"
        verbose_name = "Materiality Statement"

    def __str__(self) -> str:
        return self.report.name + " - Materiality Statement"
