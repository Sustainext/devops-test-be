from django.db import models


class MaterialChoices(models.TextChoices):
    MILLIGRAM = "Milligram", "Milligram"
    GRAM = "Gram", "Gram"
    KILOGRAM = "Kilogram", "Kilogram"
    METRIC_TON = "Metric ton", "Metric ton"
    POUND = "Pound", "Pound"
    US_SHORT_TON = "US short ton", "US short ton"
    MILLILITER = "Milliliter", "Milliliter"
    LITER = "Liter", "Liter"
    FLUID_OUNCE = "Fluid Ounce", "Fluid Ounce"
    QUART = "Quart", "Quart"
    GALLON = "Gallon", "Gallon"
    PINT = "Pint", "Pint"
    CUBIC_CENTIMETER = "Cubic centimeter", "Cubic centimeter"
    CUBIC_DECIMETER = "Cubic decimeter", "Cubic decimeter"
    CUBIC_METER = "Cubic meter", "Cubic meter"
    CUBIC_FOOT = "Cubic foot", "Cubic foot"
