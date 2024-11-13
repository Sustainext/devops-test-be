from rest_framework import serializers
from esg_report.models.ScreenSix import StakeholderEngagement
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class StakeholderEngagementSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(),
        required=False,
    )

    class Meta:
        model = StakeholderEngagement
        fields = "__all__"
