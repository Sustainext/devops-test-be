from esg_report.models.ScreenTwelve import ScreenTwelve
from rest_framework import serializers
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class ScreenTwelveSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenTwelve
        fields = "__all__"
