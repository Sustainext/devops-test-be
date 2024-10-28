from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from django.utils.translation import gettext_lazy as _


class ContentIndexRequirementOmissionReason(AbstractModel, HistoricalModelMixin):
    """
    Model for storing the reasons for omitting content index requirements.
    """

    report = models.OneToOneField("sustainapp.Report", on_delete=models.CASCADE)
    is_filled = models.BooleanField(default=False)
    reason = models.CharField(
        _("reason"),
        max_length=50,
        choices=(
            (
                "information unavailable/incomplete",
                "Information unavailable/incomplete",
            ),
            ("not applicable", "Not applicable"),
            ("legal prohibitions", "Legal prohibitions"),
            ("confidentiality constraints", "Confidentiality constraints"),
        ),
        null=True,
        blank=True,
    )
    explanation = models.TextField(_("explanation"), null=True, blank=True)
    indicator = models.CharField(_("indicator_number"), max_length=10, db_index=True)

    class Meta:
        verbose_name = _("content index requirement omission reason")
        verbose_name_plural = _("content index requirement omission reasons")
        unique_together = ("report", "indicator")
