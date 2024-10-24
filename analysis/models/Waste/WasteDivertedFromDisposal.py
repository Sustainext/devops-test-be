from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.models.AbstractModel import AbstractModel
from common.enums.WasteMeasumentUnits import MeasurementUnit
from common.enums.WasteCategoryChoices import WASTE_CATEGORY_CHOICES
from django.db import models

RECOVERY_OPTION_CHOICES = (
    ("preparation_for_reuse", "Preparation for reuse"),
    ("recyling", "Recycling"),
    ("other", "Other"),
)


class WasteDivertedFromDisposal(AbstractAnalysisModel, AbstractModel):
    waste_diverted = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        choices=MeasurementUnit.choices,
        default=MeasurementUnit.KILOGRAMS,
    )
    recovery_option = models.CharField(max_length=200, choices=RECOVERY_OPTION_CHOICES)
    waste_unit = models.CharField(max_length=50)
    waste_type = models.CharField(max_length=500)
    index = models.PositiveIntegerField()
    category = models.CharField(max_length=200, choices=WASTE_CATEGORY_CHOICES)
    site = models.CharField(max_length=100, blank=True, null=True)

    def convert_to_kilograms(self):
        conversion_factors = {
            MeasurementUnit.GRAMS: 0.001,  # 1 gram = 0.001 kg
            MeasurementUnit.KILOGRAMS: 1.0,  # 1 kg = 1 kg
            MeasurementUnit.METRIC_TONS: 1000.0,  # 1 metric ton = 1000 kg
            MeasurementUnit.US_SHORT_TON: 907.185,  # 1 US short ton = 907.185 kg
            MeasurementUnit.POUNDS: 0.453592,  # 1 lb = 0.453592 kg
        }
        return round(self.waste_diverted * conversion_factors[self.waste_unit], 2)

    def __str__(self) -> str:
        return f"{self.category} - {self.waste_type}"
