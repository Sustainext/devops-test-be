from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Location, Organization, Corporateentity
from datametric.models import RawResponse
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from logging import getLogger
from authentication.models import Client

logger = getLogger("error.log")


# Models for 1st energy screen
class BasicDataForEnergy(AbstractModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(Corporateentity, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.CharField(max_length=8)
    raw_response = models.ForeignKey(RawResponse, on_delete=models.CASCADE)
    quantiy_gj = models.DecimalField(
        max_digits=12, decimal_places=5, null=True, blank=True
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=5, null=True, blank=True
    )
    unit = models.CharField(max_length=8, null=True, blank=True)
    index = models.PositiveIntegerField(null=True, blank=True)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True,default=Client.get_default_client
    )

    class Meta:
        abstract = True

    def convert_to_gj(self, quantity, unit):
        conversion_factors = {
            "Joules": 1e-9,
            "KJ": 1e-3,
            "Wh": 0.0000036,
            "KWh": 0.0036,
            "GJ": 1,
            "MMBtu": 1.05506,
        }

        factor = conversion_factors.get(unit)
        if factor is None:
            raise ValueError(f"Unsupported unit: {unit}")

        return round(quantity * factor, 5)

    def save(self, *args, **kwargs):
        if self.quantity and self.unit:
            try:
                self.quantity_gj = self.convert_to_gj(self.quantity, self.unit)
            except ValueError as e:
                logger.error(f"Error converting quantity on Energy: {e}")
                self.quantity_gj = None
        super().save(*args, **kwargs)


class DirectPurchasedEnergy(BasicDataForEnergy):

    energy_type = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)
    purpose = models.CharField(max_length=256, null=True, blank=True)
    renewability = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"DirectPurchasedEnergy with id {self.id}"


class ConsumedEnergy(BasicDataForEnergy):

    energy_type = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)
    purpose = models.CharField(max_length=256, null=True, blank=True)
    renewability = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"ConsumedEnergy with id {self.id}"


class SelfGeneratedEnergy(BasicDataForEnergy):

    energy_type = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)
    renewability = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"SelfGenerated with id {self.id}"


class EnergySold(BasicDataForEnergy):

    energy_type = models.CharField(max_length=64, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)
    type_of_entity = models.CharField(
        max_length=64, null=True, blank=True
    )  # type_of_energy to entity_type
    name_of_entity = models.CharField(max_length=128, null=True, blank=True)
    renewability = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"EnergySold with id {self.id}"


# Models for 2nd energy screen
class EnergyConsumedOutsideOrg(BasicDataForEnergy):
    energy_type = models.CharField(max_length=64, null=True, blank=True)
    purpose = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"EnergyConsumedOutsideOrg with id {self.id}"


# Models for 3rd energy screen
class EnergyIntensity(AbstractAnalysisModel, AbstractModel):
    energy_type = models.CharField(max_length=64, null=True, blank=True)
    energy_quantity = models.DecimalField(
        max_digits=20, decimal_places=5, null=True, blank=True
    )
    energy_unit = models.CharField(max_length=1024, null=True, blank=True)
    org_metric = models.CharField(max_length=64, null=True, blank=True)
    metric_quantity = models.DecimalField(
        max_digits=20, decimal_places=5, null=True, blank=True
    )
    metric_unit = models.CharField(max_length=32, null=True, blank=True)
    index = models.PositiveIntegerField(null=True, blank=True)
    raw_response = models.ForeignKey(RawResponse, on_delete=models.CASCADE)

    def __str__(self):
        return f"EnergyIntensity with id {self.id}"


class ReductionEnergyConsumption(BasicDataForEnergy):
    type_of_intervention = models.CharField(max_length=64, null=True, blank=True)
    energy_type_reduced = models.CharField(max_length=64, null=True, blank=True)
    base_year = models.PositiveIntegerField(null=True, blank=True)
    energy_reduction = models.CharField(max_length=32, null=True, blank=True)
    methodology_used = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"ReductionEnergyConsumption with id {self.id}"


# Models for 5th Energy Screen
class ReductionEnergyInProductServices(BasicDataForEnergy):
    product = models.CharField(max_length=128, null=True, blank=True)
    base_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"ReductionInProductServices with id {self.id}"
