from django.db import models
from common.models.AbstractModel import AbstractModel

# Create your models here.
from sustainapp.models import Corporateentity, Organization, Framework
from authentication.models import Client


class ESGReport(AbstractModel):
    """
    ESG Report Model
    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="esg_reports"
    )
    corporate_entity = models.ForeignKey(
        Corporateentity,
        on_delete=models.SET_NULL,
        related_name="esg_reports",
        null=True,
        blank=True,
    )
    framework = models.ForeignKey(
        Framework, on_delete=models.PROTECT, related_name="framework_esg_reports"
    )
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="client_esg_reports"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"ESG Report for {self.organization.name} ({self.framework.name})"
