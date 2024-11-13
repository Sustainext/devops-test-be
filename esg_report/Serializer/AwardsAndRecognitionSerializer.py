from rest_framework import serializers
from esg_report.models.ScreenFive import AwardAndRecognition
from common.Serializer.Fields.ClientFilteredPrimaryKeyRelatedField import (
    ClientFilteredPrimaryKeyRelatedField,
)
from sustainapp.models import Report

class AwardsAndRecognitionSerializer(serializers.ModelSerializer):
    report = ClientFilteredPrimaryKeyRelatedField(
        queryset=Report.objects.all(),
        required=False,
    )

    class Meta:
        model = AwardAndRecognition
        fields = "__all__"
