from rest_framework import serializers
from esg_report.models import ESGReportIntroduction


class ESGReportIntroductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESGReportIntroduction
        fields = "__all__"


class GetESGReportIntroductionBySectionType(serializers.ModelSerializer):
    class Meta:
        model = ESGReportIntroduction
        fields = ["section_type"]
