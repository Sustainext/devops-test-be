from esg_report.models.ScreenFour import SustainabilityRoadmap
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from rest_framework import serializers
from sustainapp.models import Report


class SustainabilityRoadmapSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = SustainabilityRoadmap
        fields = "__all__"
