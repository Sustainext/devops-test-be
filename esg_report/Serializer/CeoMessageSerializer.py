from rest_framework import serializers
from esg_report.models.ScreenOne import CeoMessage
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class CeoMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the CEO Message model
    """

    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = CeoMessage
        fields = "__all__"
