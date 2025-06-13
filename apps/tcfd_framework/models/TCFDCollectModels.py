from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Organization, Corporateentity


class CoreElements(AbstractModel, HistoricalModelMixin):
    """
    Model to represent the core elements of TCFD Collect Section.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Name of the core element."
    )
    description = models.TextField(help_text="Description of the core element.")

    def __str__(self):
        return self.name


class RecommendedDisclosures(AbstractModel, HistoricalModelMixin):
    """
    Model to represent the recommended disclosures of TCFD Collect Section.
    """

    description = models.TextField(
        help_text="Description of the recommended disclosure."
    )
    order = models.PositiveIntegerField(
        help_text="Order of the recommended disclosure in the list."
    )
    core_element = models.ForeignKey(
        CoreElements,
        on_delete=models.CASCADE,
        related_name="disclosures",
        help_text="Core element to which this disclosure belongs.",
    )
    screen_tag = models.CharField(null=True, blank=True, max_length=5)

    def __str__(self):
        return f"{self.core_element.name} - {self.description[:50]}"

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Recommended Disclosures"


class DataCollectionScreen(AbstractModel, HistoricalModelMixin):
    """
    Model to represent the data collection screen for TCFD Collect Section.
    """

    name = models.CharField(
        max_length=255, help_text="Name of the data collection screen."
    )
    recommended_disclosure = models.ForeignKey(
        RecommendedDisclosures,
        on_delete=models.CASCADE,
        related_name="data_collection_screens",
        help_text="Recommended disclosure to which this screen belongs.",
    )
    order = models.PositiveIntegerField(
        help_text="Order of the data collection screen in the list."
    )

    def __str__(self):
        return f"{self.name} - {self.recommended_disclosure.description[:50]}"

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Data Collection Screens"


class SelectedDisclosures(AbstractModel, HistoricalModelMixin):
    """
    Model to get selected recommended disclosures as per organization and corporate entity.
    """

    recommended_disclosure = models.ForeignKey(
        RecommendedDisclosures,
        on_delete=models.CASCADE,
        related_name="selected_disclosures",
        help_text="Recommended disclosure that has been selected.",
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(
        Corporateentity, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.recommended_disclosure.description[:50]} - {self.data_collection_screen.name}"
