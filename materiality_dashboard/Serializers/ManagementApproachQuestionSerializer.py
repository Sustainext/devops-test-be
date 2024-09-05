from rest_framework import serializers
from materiality_dashboard.models import ManagementApproachQuestion


class ManagementApproachQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementApproachQuestion
        fields = "__all__"
