from django.db import models


class WaterUnitChoices(models.TextChoices):
    LITRE = "Litre", "Litre"
    MEGALITRE = "Megalitre", "Megalitre"
    CUBIC_METER = "Cubic meter", "Cubic meter"
    KILOLITRE = "Kilolitre", "Kilolitre"
    MILLION_LITRES_PER_DAY = "Million litres per day", "Million litres per day"
