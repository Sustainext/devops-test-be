from rest_framework import serializers
from materiality_dashboard.models import MaterialityAssessment


class MaterialityAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityAssessment
        fields = [
            "id",
            "organization",
            "corporate",
            "start_date",
            "end_date",
            "framework",
            "approach",
            "status",
        ]
        read_only_fields = ["client"]
