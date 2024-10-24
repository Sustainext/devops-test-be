from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class ScreenTen(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_ten"
    )
    company_sustainability_statement = models.TextField(null=True, blank=True)
    approach_for_sustainability = models.TextField(null=True, blank=True)
    sustainability_goals = models.TextField(null=True, blank=True)
    approach_to_supply_chain_sustainability = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "screen_ten"
        verbose_name = "Screen Ten"
        verbose_name_plural = "Screen Ten"

    def __str__(self):
        return f"{self.company_sustainability_statement}"
