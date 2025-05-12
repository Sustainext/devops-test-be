from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class CanadaBasicModel(models.Model):
    """
    Common model that has
    1. Organization for organization select, cannot be ignored.
    2. Corporate entity for corporate entity select, can be ignored.
    3. year for representing year.
    4. status for representing status of the model.
    """
    organization = models.ForeignKey("sustainapp.Organization", on_delete=models.CASCADE)
    corporate = models.ForeignKey("sustainapp.Corporateentity", on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(validators=[MaxValueValidator(2100), MinValueValidator(2000)])
    status = models.CharField(max_length=20, default="incomplete", choices=[('completed', 'Completed'), ('incomplete', 'Incomplete'), ('in_progress', 'In Progress')])

    class Meta:
        abstract = True
