from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.enums.WaterEnums import WaterUnitChoices

class WaterFromStressAreas(AbstractAnalysisModel, AbstractModel):
    source = models.CharField(max_length=100)
    water_type = models.CharField(max_length=100)
    water_unit = models.CharField(max_length=100)
    business_operation = models.CharField(max_length=100)
    name_of_water_stress_area = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=100)
    total_water_withdrawal = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=WaterUnitChoices.choices,
        default=WaterUnitChoices.MEGALITRE,
    )
    total_water_discharge = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=WaterUnitChoices.choices,
        default=WaterUnitChoices.MEGALITRE,
    )
    index = models.PositiveIntegerField()

    def convert_to_megalitres(self,field_name):
        conversion_factors = {
        WaterUnitChoices.LITRE: 1e-6,
        WaterUnitChoices.CUBIC_METER: 1e-3,
        WaterUnitChoices.KILOLITRE: 1e-3,
        WaterUnitChoices.MILLION_LITRES_PER_DAY: 1,
        WaterUnitChoices.MEGALITRE: 1,
    }

        field_value = getattr(self, field_name)
        conversion_factor = conversion_factors.get(self.water_unit, 1)
        converted_value = float(field_value) * conversion_factor
        return round(converted_value, 6)
    
    def __str__(self) -> str:
        return f"{self.source} - {self.water_type}"

class WaterDischargeFromStressAreas(AbstractAnalysisModel, AbstractModel):
    withdraw_from_third_party = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=WaterUnitChoices.choices,
        default=WaterUnitChoices.MEGALITRE,
    )
    index = models.PositiveIntegerField()

    def convert_to_megalitres(self,field_name):
        conversion_factors = {
        WaterUnitChoices.LITRE: 1e-6,
        WaterUnitChoices.CUBIC_METER: 1e-3,
        WaterUnitChoices.KILOLITRE: 1e-3,
        WaterUnitChoices.MILLION_LITRES_PER_DAY: 1,
        WaterUnitChoices.MEGALITRE: 1,
    }

        field_value = getattr(self, field_name)
        conversion_factor = conversion_factors.get(self.unit, 1)
        converted_value = float(field_value) * conversion_factor
        return round(converted_value, 6)
    
    def __str__(self) -> str:
        return f"{self.source} - {self.withdraw_from_third_party}"
