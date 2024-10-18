from rest_framework import serializers
from esg_report.models.ScreenFifteen import ScreenFifteenModel
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class ScreenFifteenSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenFifteenModel
        fields = "__all__"
