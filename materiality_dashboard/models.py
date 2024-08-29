from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Organization, Corporateentity, Framework
from authentication.models import Client


# Materiality Assessment Model
class MaterialityAssessment(AbstractModel):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("outdated", "Outdated"),
        ("archived", "Archived"),
    ]

    APPROACH_CHOICES = [
        ("In accordance with", "In accordance with"),
        ("With Reference to", "With Reference to"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    corporate = models.ForeignKey(
        Corporateentity, on_delete=models.SET_NULL, null=True, blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    approach = models.CharField(
        max_length=100, choices=APPROACH_CHOICES, null=True, blank=True
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="in_progress"
    )

    # * created_by, last_updated_by
    def __str__(self):
        return (
            f"{self.client.name} - {self.organization.name} - {self.reporting_period}"
        )

    @property
    def topic_summary(self):
        # Returns a summary of selected topics
        return ", ".join([str(topic.topic) for topic in self.selected_topics.all()])

    @property
    def disclosure_summary(self):
        # Returns a summary of selected disclosures
        return ", ".join(
            [
                str(disclosure.disclosure)
                for disclosure in AssessmentDisclosureSelection.objects.filter(
                    topic_selection__assessment=self
                )
            ]
        )


class MaterialTopic(AbstractModel):
    """
    Stores the material topics in accordance with their framework for the materiality assessment
    """

    # ? Should we add path to the material topic? Since One Material Topic can have many paths.
    name = models.CharField(max_length=255)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Disclosure(AbstractModel):
    """
    Stores the disclosures in accordance with their topic for the materiality assessment Eg. G301-and G301-b
    """

    topic = models.ForeignKey(MaterialTopic, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.topic.name} - {self.description[:50]}"


class AssessmentTopicSelection(AbstractModel):
    """
    Represents the selection of material topics for a specific materiality assessment.

    Each `MaterialityAssessment` can have multiple `AssessmentTopicSelection` objects, each
    representing a selected material topic for that assessment.
    """

    assessment = models.ForeignKey(
        MaterialityAssessment, on_delete=models.CASCADE, related_name="selected_topics"
    )
    topic = models.ForeignKey(MaterialTopic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.assessment} - {self.topic}"


# Assessment Disclosure Selection Model
class AssessmentDisclosureSelection(AbstractModel):
    topic_selection = models.ForeignKey(
        AssessmentTopicSelection,
        on_delete=models.CASCADE,
        related_name="selected_disclosures",
    )
    disclosure = models.ForeignKey(Disclosure, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.topic_selection} - {self.disclosure}"


# Materiality Change Confirmation Model
class MaterialityChangeConfirmation(AbstractModel):
    assessment = models.OneToOneField(
        MaterialityAssessment,
        on_delete=models.CASCADE,
        related_name="change_confirmation",
    )
    change_made = models.BooleanField()
    reason_for_change = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.assessment} - {'Change Made' if self.change_made else 'No Change'}"
        )


# Stakeholder Model for capturing different types of stakeholders
class StakeholderEngagement(AbstractModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Materiality Assessment Process Model
class MaterialityAssessmentProcess(AbstractModel):
    assessment = models.ForeignKey(
        MaterialityAssessment,
        on_delete=models.CASCADE,
        related_name="assessment_process",
    )
    process_description = models.TextField(null=True, blank=True)
    impact_assessment_process = models.TextField(null=True, blank=True)

    stakeholder_others = models.TextField(
        blank=True, null=True
    )  # Text field for "Others please specify" input
    selected_stakeholders = models.ManyToManyField(
        StakeholderEngagement, blank=True
    )  # Relationship to stakeholders

    def __str__(self):
        return f"{self.assessment} - Materiality Assessment Process"


# Impact Type Model
class ImpactType(AbstractModel):
    """
    This model is used for storing the different types of impacts that can be associated with a material topic. example Environmental, Social or Governance.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Materiality Impact Model
class MaterialityImpact(AbstractModel):
    assessment = models.ForeignKey(
        MaterialityAssessment,
        on_delete=models.CASCADE,
        related_name="management_impacts",
    )
    material_topic = models.ForeignKey(MaterialTopic, on_delete=models.CASCADE)
    impact_type = models.ForeignKey(ImpactType, on_delete=models.SET_NULL, null=True)
    impact_overview = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.assessment} - {self.material_topic} - {self.impact_type}"


# Management Approach Question Model
class ManagementApproachQuestion(AbstractModel):
    assessment = models.ForeignKey(
        MaterialityAssessment,
        on_delete=models.CASCADE,
        related_name="management_approach_questions",
    )
    question_text = models.TextField()
    answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.assessment} - {self.question_text[:50]}"
