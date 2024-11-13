from sustainapp.models import Location, Organization, Corporateentity
from django.db import models
from datametric.models import RawResponse
from authentication.models import Client


class AbstractAnalysisModel(models.Model):
    month = models.IntegerField(null=True)
    year = models.IntegerField()
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    corporate = models.ForeignKey(Corporateentity, on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    raw_response = models.ForeignKey(RawResponse, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True,default=Client.get_default_client)

    class Meta:
        abstract = True
