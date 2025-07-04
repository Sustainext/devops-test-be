from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin


class ScreenFourteen(AbstractModel, HistoricalModelMixin):
    report = models.OneToOneField(
        "sustainapp.Report",
        on_delete=models.CASCADE,
        related_name="screen_fourteen",
    )
    community_engagement = models.JSONField(
        verbose_name="Community Engagement Statement",
        help_text="Add a statement about the company's community engagement.",
        null=True,
        blank=True,
    )

    # Field to store the impact assessment statement
    impact_assessment = models.JSONField(
        verbose_name="Impact Assessment",
        help_text="Add a statement about the company's impact assessment.",
        null=True,
        blank=True,
    )

    # Field to store the company's CSR policies statement
    csr_policies = models.JSONField(
        verbose_name="Corporate Social Responsibility Policies",
        help_text="Add a statement about the company's Corporate Social Responsibility policies.",
        null=True,
        blank=True,
    )

    violation_rights=models.JSONField(
        verbose_name="Incidents of Violation of Rights of Indigenous People",
        help_text="Add statement about company’s policy on violation of rights of indigenous people",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Screen Fourteen for Report ID: {self.report.id}"

    class Meta:
        verbose_name = "Screen Fourteen"
        verbose_name_plural = "Screen Fourteen"
