from rest_framework import serializers
from esg_report.models.ScreenThree import MissionVisionValues
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class MissionVisionValuesSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = MissionVisionValues
        fields = "__all__"
