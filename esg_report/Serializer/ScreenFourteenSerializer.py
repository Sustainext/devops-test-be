from esg_report.models.ScreenFourteen import ScreenFourteen
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report
from rest_framework import serializers


class ScreenFourteenSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenFourteen
        fields = "__all__"
