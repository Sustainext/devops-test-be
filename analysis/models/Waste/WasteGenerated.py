from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.models.AbstractModel import AbstractModel
from common.enums.WasteMeasumentUnits import MeasurementUnit
from common.enums.WasteCategoryChoices import WASTE_CATEGORY_CHOICES
from django.db import models


class WasteGenerated(AbstractAnalysisModel, AbstractModel):
    category = models.CharField(max_length=200, choices=WASTE_CATEGORY_CHOICES)
    waste_generated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        choices=MeasurementUnit.choices,
        default=MeasurementUnit.KILOGRAMS,
    )
    waste_unit = models.CharField(max_length=50)
    waste_type = models.CharField(max_length=500)
    index = models.PositiveIntegerField()

    def convert_to_kilograms(self):
        conversion_factors = {
            MeasurementUnit.GRAMS: 0.001,  # 1 gram = 0.001 kg
            MeasurementUnit.KILOGRAMS: 1.0,  # 1 kg = 1 kg
            MeasurementUnit.METRIC_TONS: 1000.0,  # 1 metric ton = 1000 kg
            MeasurementUnit.US_SHORT_TON: 907.185,  # 1 US short ton = 907.185 kg
            MeasurementUnit.POUNDS: 0.453592,  # 1 lb = 0.453592 kg
        }
        return round(self.waste_generated * conversion_factors[self.waste_unit],2)

    def __str__(self):
        return f"{self.category} - {self.waste_type}"
