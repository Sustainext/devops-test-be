from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel
from django.db import models


class CeoMessage(AbstractModel):
    """
    This model stores the CEO message for an ESG Report.
    It contains fields such as:
    message
    message_image

    """

    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="ceo_message"
    )
    message = models.TextField(null=True, blank=True)
    message_image = models.TextField(null=True, blank=True)
    signature_image = models.TextField(null=True, blank=True)
    ceo_name = models.TextField(null=True, blank=True)
    signature_image_name = models.TextField(null=True, blank=True)
    message_image_name = models.TextField(null=True, blank=True)
    company_name = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"CEO Message for {self.report.organization.name}"
