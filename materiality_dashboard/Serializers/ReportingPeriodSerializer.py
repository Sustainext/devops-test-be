from rest_framework import serializers
from materiality_dashboard.models import ReportingPeriod


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = "__all__"
