from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from django.db import models

OPERATION_CHOICES = (
    ("Social impact assessments", "social_impact_assessments"),
    ("Environmental impact assessments", "environmental_impact_assessments"),
    ("Public disclosure", "public_disclosure"),
    ("Community development programs", "community_development_programs"),
    ("Stakeholder engagement plans", "stakeholder_engagement_plans"),
    (
        "Local community consultation committes",
        "local_community_consultation_committes",
    ),
    (
        "Works councils, occupational health and safety committees",
        "works_councils,_occupational_health_and_safety_committees",
    ),
    ("Community grievance processes", "community_grievance_processes"),
)


class CommunityDevelopmentNumberOfOperation(AbstractAnalysisModel, AbstractModel):
    name_of_operation = models.CharField(max_length=500, choices=OPERATION_CHOICES)
    local_community_operations_count = models.PositiveIntegerField(
        help_text="Number of operations implemented by engaging local communities"
    )
    total_operations_count = models.PositiveIntegerField(
        help_text="Total number of operations"
    )
    index = models.PositiveIntegerField(help_text="Index of the operation", default=0)

    def __str__(self):
        return f"{self.name_of_operation} - {self.local_community_operations_count}"
