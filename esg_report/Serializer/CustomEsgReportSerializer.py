from rest_framework import serializers
from esg_report.models.ESGCustomReport import EsgCustomReport


class CustomEsgReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsgCustomReport
        fields = "__all__"
