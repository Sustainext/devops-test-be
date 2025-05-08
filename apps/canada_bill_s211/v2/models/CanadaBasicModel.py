from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class CanadaBasicModel(models.Model):
    organization = models.ForeignKey("sustainapp.Organization", on_delete=models.CASCADE)
    corporate = models.ForeignKey("sustainapp.Corporateentity", on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(validators=[MaxValueValidator(2100), MinValueValidator(2000)])

    class Meta:
        abstract = True
