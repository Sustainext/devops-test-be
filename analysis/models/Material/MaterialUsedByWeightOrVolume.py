from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from common.enums.MaterialEnums import MaterialChoices


class NonRenewableMaterials(AbstractAnalysisModel, AbstractModel):
    type_of_material = models.CharField(max_length=100)
    material_used = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=MaterialChoices.choices,
        default=MaterialChoices.MILLIGRAM,
    )
    unit = models.CharField(max_length=100)
    index = models.PositiveIntegerField()
    data_source = models.CharField(max_length=100)

    conversion_factors = {
        "Milligram": 1e-3,  # to grams (g)
        "Gram": 1,  # grams is the base unit for weight
        "Kilogram Kg": 1e3,  # to grams (g)
        "Metric ton": 1e6,  # to grams (g)
        "Pound Lb": 453.592,  # to grams (g)
        "US short ton (tn)": 907184.74,  # to grams (g)
        "Milliliter": 1,  # milliliter is the base unit for liquid volume
        "Liter": 1e3,  # to milliliters (ml)
        "Fluid Ounce fl Oz": 29.5735,  # to milliliters (ml)
        "Quart Qt": 946.353,  # to milliliters (ml)
        "Gallon Gal": 3785.41,  # to milliliters (ml)
        "Pint Pt": 473.176,  # to milliliters (ml)
        "Cubic centimeter cm3": 1,  # cubic centimeter is the base unit for cubic volume
        "Cubic decimeter dm3": 1e3,  # to cubic centimeters (cm³)
        "Cubic meter m3": 1e6,  # to cubic centimeters (cm³)
        "Cubic foot ft3": 28316.8,  # to cubic centimeters (cm³)
    }

    # Define the base units for each type of unit (weight, volume, cubic volume)
    base_units = {
        "weight": "Kilogram Kg",
        "volume": "Liter",
        "cubic_volume": "Cubic meter m3",
    }

    # Unit hierarchy for dynamically detecting categories
    unit_hierarchy = {
        "weight": [
            "Milligram",
            "Gram",
            "Kilogram Kg",
            "Metric ton",
            "Pound Lb",
            "US short ton (tn)",
        ],
        "volume": [
            "Milliliter",
            "Liter",
            "Fluid Ounce fl Oz",
            "Quart Qt",
            "Gallon Gal",
            "Pint Pt",
        ],
        "cubic_volume": [
            "Cubic centimeter cm3",
            "Cubic decimeter dm3",
            "Cubic meter m3",
            "Cubic foot ft3",
        ],
    }

    def get_base_unit(self, unit):
        """Determines the base unit based on the type of unit (weight, volume, cubic volume)."""
        for category, units in self.unit_hierarchy.items():
            if unit in units:
                return self.base_units[category]
        raise ValueError(f"Unit '{unit}' does not belong to any known category")

    def convert(self, value, from_unit, to_unit=None):
        """Converts `value` from `from_unit` to the target unit. Automatically detects base units if `to_unit` is None."""
        if from_unit not in self.conversion_factors:
            raise ValueError(f"Unsupported conversion from {from_unit}")

        # Determine the target unit if not specified (use base unit for the category)
        if to_unit is None:
            to_unit = self.get_base_unit(from_unit)

        if to_unit not in self.conversion_factors:
            raise ValueError(f"Unsupported conversion to {to_unit}")

        # Convert the value to the base unit first
        base_value = value * self.conversion_factors[from_unit]

        # Convert the base value to the desired unit
        converted_value = base_value / self.conversion_factors[to_unit]
        return converted_value


class RenewableMaterials(AbstractAnalysisModel, AbstractModel):
    type_of_material = models.CharField(max_length=100)
    material_used = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        choices=MaterialChoices.choices,
        default=MaterialChoices.MILLIGRAM,
    )
    unit = models.CharField(max_length=100)
    index = models.PositiveIntegerField()
    data_source = models.CharField(max_length=100)
