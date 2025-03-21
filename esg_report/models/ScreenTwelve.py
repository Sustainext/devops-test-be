from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class ScreenTwelve(AbstractModel, HistoricalModelMixin):
    """
    This model represents the screen twelve of the ESG report.
    """

    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_twelve"
    )
    environmental_responsibility_statement = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's responsibility to minimize the environmental impact",
    )
    emissions = models.JSONField(
        blank=True,
        null=True,
        help_text="Description of the company's efforts to reduce emissions",
    )
    scope_one_emissions = models.JSONField(
        blank=True,
        null=True,
        help_text="Add statement about company’s scope 1 emissions",
    )
    scope_two_emissions = models.JSONField(
        blank=True,
        null=True,
        help_text="Add statement about company’s scope 2 emissions",
    )
    scope_three_emissions = models.JSONField(
        blank=True,
        null=True,
        help_text="Add statement about company’s scope 3 emissions",
    )
    ghg_emission_intensity_tracking = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about tracking of GHG emission intensity",
    )
    ghg_emission_reduction_efforts = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about efforts to reduce GHG emissions",
    )
    ozone_depleting_substance_elimination = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's commitment to eliminate use of ozone depleting substances",
    )
    material_management_strategy = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's material management strategy",
    )
    recycling_process = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's process for recycling",
    )
    reclamation_recycling_process = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's reclamation and recycling process",
    )
    water_withdrawal_tracking = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's tracking of water withdrawal",
    )
    water_consumption_goals = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's water consumption goals",
    )
    energy_consumption_within_organization = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's energy consumption within the organization",
    )
    energy_consumption_outside_organization = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's energy consumption outside of the organization",
    )
    energy_intensity_tracking = models.JSONField(
        blank=True, null=True, help_text="Statement about tracking the Energy Intensity"
    )
    energy_consumption_reduction_commitment = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's commitment to reduce energy consumption",
    )
    significant_spills = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's significant spills",
    )
    habitat_protection_restoration_commitment = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's commitment to protect and restore habitats",
    )
    air_quality_protection_commitment = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's commitment to protect and maintain air quality",
    )
    biogenic_c02_emissions = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's biogenic CO2 emissions",
    )
    biogenic_c02_emissions_305_3c = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's biogenic CO2 emissions 305 3c",
    )
    consolidation = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's consolidation",
    )
    base_year = models.JSONField(
        blank=True,
        null=True,
        help_text="Statement about company's base year",
    )

    class Meta:
        verbose_name = "Screen Twelve"
        verbose_name_plural = "Screen Twelve"

    def __str__(self):
        return f"Screen Twelve for {self.report.client.name} for {self.report.start_date} to {self.report.end_date}"
