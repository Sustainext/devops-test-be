from sustainapp.models import Location, Organization, Corporateentity
from django.db import models


class AbstractAnalysisModel(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(Corporateentity, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        abstract = True
