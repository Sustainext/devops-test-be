from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from analysis.models.Social.Gender import Gender


class EcoStandardWages(AbstractAnalysisModel, AbstractModel):
    currency = models.CharField(max_length=255, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT, null=True, blank=True)
    value = models.PositiveBigIntegerField(null=True, blank=True)
    minimum_wage = models.PositiveBigIntegerField(null=True, blank=True)
    minimum_wage_currency = models.CharField(max_length=255, null=True, blank=True)
    index = models.PositiveBigIntegerField(null=True, blank=True)
