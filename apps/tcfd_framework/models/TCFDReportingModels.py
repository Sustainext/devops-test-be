from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin


class TCFDReportingInformation(AbstractModel, HistoricalModelMixin):
    SECTOR_TYPE_CHOICES = [
        ("financial", "Financial Sector"),
        ("non_financial", "Non-Financial Sector"),
    ]
    client = models.ForeignKey("authentication.Client", on_delete=models.CASCADE)
    organization = models.ForeignKey(
        "sustainapp.Organization", on_delete=models.CASCADE
    )
    corporate = models.ForeignKey(
        "sustainapp.Corporateentity", null=True, blank=True, on_delete=models.SET_NULL
    )
    sector_type = models.CharField(max_length=20, choices=SECTOR_TYPE_CHOICES)
    sector = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Only required if sector_type is 'financial'",
    )
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.BooleanField(
        default=False, help_text="Indicates if the reporting information is complete"
    )

    def __str__(self):
        return f"{self.organization} ({self.get_sector_type_display()}) {self.from_date} - {self.to_date}"
