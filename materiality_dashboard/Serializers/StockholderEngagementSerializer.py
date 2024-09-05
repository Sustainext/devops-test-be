from rest_framework import serializers
from materiality_dashboard.models import StakeholderEngagement


class StakeholderEngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeholderEngagement
        fields = "__all__"
