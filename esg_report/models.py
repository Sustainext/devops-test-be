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


class ESGReportIntroduction(AbstractModel):
    INTRO_SECTION_CHOICES = [
        ("message_from_ceo", "Message from CEO/MD/Chairman"),
        ("about_company", "About the Company & Operations"),
        ("business_model", "Business Model and Impact"),
        (
            "activities_value_chain",
            "Activities, Value Chain, and Other Business Relationships",
        ),
        (
            "entities_included",
            "Entities Included in the Organization's Sustainability Reporting",
        ),
        ("supply_chain", "Supply Chain"),
        ("mission_vision_values", "Mission, Vision, Values"),
        ("position_statement", "Position Statement"),
        ("sustainability_roadmap", "Sustainability Roadmap"),
        ("awards_alliances", "Awards & Alliances"),
        ("stakeholder_engagement", "Stakeholder Engagement"),
    ]

    esg_report = models.ForeignKey(
        ESGReport, on_delete=models.CASCADE, related_name="introductions"
    )
    section_type = models.CharField(max_length=50, choices=INTRO_SECTION_CHOICES)
    content = models.TextField()
    attachment = models.FileField(
        upload_to="esg_report_attachments/", null=True, blank=True
    )

    class Meta:
        unique_together = ("esg_report", "section_type")
