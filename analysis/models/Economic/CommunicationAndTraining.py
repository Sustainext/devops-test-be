from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from sustainapp.models import Location, Organization, Corporateentity

AntiCorruptionInfo1 = [
    (
        "communicated anti-corruption policy - region",
        "Communicated anti-corruption policy - region",
    ),
    (
        "received training on anti-corruption - region",
        "Received training on anti-corruption - region",
    ),
]

AntiCorruptionInfo2 = [
    (
        "communicated anti-corruption policy - emp category",
        "Communicated anti-corruption policy - Employee Category",
    ),
    (
        "communicated anti-corruption policy - business partner",
        "Communicated anti-corruption policy - Business Partner",
    ),
    (
        "received training on anti-corruption - region",
        "Received training on anti-corruption - Region",
    ),
]

BusinessPartnerOrEmpCategory = [
    ("emp category", "Employee Category"),
    ("business partner", "Business Partner"),
]


class EcoTotalBodyMembers(AbstractModel, AbstractAnalysisModel):
    location_name = models.CharField(max_length=255, null=True, blank=True)
    index = models.PositiveBigIntegerField(null=True, blank=True)
    table_name = models.CharField(max_length=255, choices=AntiCorruptionInfo1)
    specific_total = models.PositiveBigIntegerField(null=True, blank=True)
    total = models.PositiveBigIntegerField(null=True, blank=True)


class EcoTotalBodyMembersRegion(AbstractModel, AbstractAnalysisModel):
    location_name = models.CharField(max_length=255, null=True, blank=True)
    index = models.PositiveBigIntegerField(null=True, blank=True)
    table_name = models.CharField(max_length=255, choices=AntiCorruptionInfo2)
    emp_category_or_business_partner = models.CharField(
        max_length=32, choices=BusinessPartnerOrEmpCategory
    )
    specific_total = models.PositiveBigIntegerField(null=True, blank=True)
    total = models.PositiveBigIntegerField(null=True, blank=True)
