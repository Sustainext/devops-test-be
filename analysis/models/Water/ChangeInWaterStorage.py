from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.enums.WaterEnums import WaterUnitChoices

class ChangeInWaterStorage(AbstractAnalysisModel, AbstractModel):
    unit = models.CharField(max_length=100)
    total_water_storage_at_end = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=WaterUnitChoices.choices,
        default=WaterUnitChoices.MEGALITRE,
    )
    total_water_storage_at_beginning = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=WaterUnitChoices.choices,
        default=WaterUnitChoices.MEGALITRE,
    )
    change_in_water_storage = models.DecimalField(
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