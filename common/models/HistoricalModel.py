from django.db import models
from simple_history.models import HistoricalRecords


class HistoricalModelMixin(models.Model):
    """
    A model mixin that provides historical records.
    """

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
