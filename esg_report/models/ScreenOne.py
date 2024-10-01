from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel
from django.db import models


class CeoMessage(AbstractModel):
    """
    This model stores the CEO message for an ESG Report.
    It contains fields such as:
    message
    message_image
    signature
    signature_image
    """

    esg_report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="ceo_message"
    )
    message = models.TextField()
    message_image = models.ImageField(upload_to="esg_report/ceo_message/")
    signature = models.CharField(max_length=255)
    signature_image = models.ImageField(upload_to="esg_report/ceo_message/")

    def __str__(self):
        return f"CEO Message for {self.esg_report.organization.name} ({self.esg_report.framework.name})"
