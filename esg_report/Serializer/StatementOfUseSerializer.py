from rest_framework import serializers
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report
from esg_report.models.StatementOfUse import StatementOfUseModel


class StatementOfUseSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = StatementOfUseModel
        fields = "__all__"
