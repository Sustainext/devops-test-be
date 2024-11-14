from sustainapp.models import Report
from rest_framework import serializers
from esg_report.models.ScreenTen import ScreenTen
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)


class ScreenTenSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = ScreenTen
        fields = "__all__"
        read_only_fields = ["id"]
