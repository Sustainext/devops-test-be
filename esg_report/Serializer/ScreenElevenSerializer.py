from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from rest_framework import serializers
from esg_report.models.ScreenEleven import ScreenEleven
from sustainapp.models import Report


class ScreenElevenSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenEleven
        fields = "__all__"

    def __str__(self) -> str:
        return f"{self.report} - Screen Eleven"
