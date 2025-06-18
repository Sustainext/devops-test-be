from rest_framework import serializers
from apps.tcfd_framework.report.models import TCFDReport


class TCFDReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCFDReport
        fields = "__all__"
