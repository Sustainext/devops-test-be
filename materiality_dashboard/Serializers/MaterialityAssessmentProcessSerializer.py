from rest_framework import serializers
from materiality_dashboard.models import (
    MaterialityAssessmentProcess,
    StakeholderEngagement,
)


class MaterialityAssessmentProcessSerializer(serializers.ModelSerializer):
    selected_stakeholders = serializers.PrimaryKeyRelatedField(
        queryset=StakeholderEngagement.objects.all(), many=True, required=False
    )

    class Meta:
        model = MaterialityAssessmentProcess
        fields = [
            "assessment",
            "process_description",
            "impact_assessment_process",
            "stakeholder_others",
            "selected_stakeholders",
        ]
