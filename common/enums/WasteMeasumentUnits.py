from django.db import models


class MeasurementUnit(models.TextChoices):
    GRAMS = "g", "grams"
    KILOGRAMS = "Kgs", "kilograms"
    METRIC_TONS = "t (metric tons)", "metric tons"
    US_SHORT_TON = "ton (US short ton)", "US short ton"
    POUNDS = "lbs", "pounds"
