from rest_framework import serializers
from esg_report.models.ScreenTwo import AboutTheCompanyAndOperations
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report


class AboutTheCompanyAndOperationsSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(), required=False
    )

    class Meta:
        model = AboutTheCompanyAndOperations
        fields = "__all__"
