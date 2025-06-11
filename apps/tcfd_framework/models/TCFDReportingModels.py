from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin

class Sector(AbstractModel, HistoricalModelMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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
    sector = models.ForeignKey(
        Sector,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Only required if sector_type is 'financial'",
    )
    from_date = models.DateField()
    to_date = models.DateField()

    def __str__(self):
        return f"{self.organization} ({self.get_sector_type_display()}) {self.from_date} - {self.to_date}"

    def clean(self):
        from rest_framework.exceptions import ValidationError

        # sector is required if sector_type is financial
        if self.sector_type == "financial" and not self.sector:
            raise ValidationError(
                {"sector": "This field is required when sector type is Financial."}
            )
        # sector must be null if sector_type is non_financial
        if self.sector_type == "non_financial" and self.sector:
            raise ValidationError(
                detail={
                    "sector": "This field must be empty when sector type is Non-Financial."
                }
            )
        if (
            hasattr(self.organization, "client_id")
            and self.organization.client_id != self.client_id
        ):
            raise ValidationError(
                {
                    "organization": "Selected Organization does not belong to the selected Client."
                }
            )
        if self.corporate:
            if (
                hasattr(self.corporate.organization, "client_id")
                and self.corporate.organization.client_id != self.client_id
            ):
                raise ValidationError(
                    {
                        "corporate": "Selected Corporate does not belong to the selected Client."
                    }
                )
