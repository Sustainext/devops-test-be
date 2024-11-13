from rest_framework import serializers
from esg_report.models.ContentIndexRequirementOmissionReason import (
    ContentIndexRequirementOmissionReason,
)


class ContentIndexRequirementOmissionReasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentIndexRequirementOmissionReason
        fields = "__all__"
