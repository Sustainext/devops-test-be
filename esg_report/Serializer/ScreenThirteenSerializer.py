from esg_report.models.ScreenThirteen import ScreenThirteen
from rest_framework import serializers
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class ScreenThirteenSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenThirteen
        fields = "__all__"
