from rest_framework import serializers
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation

class SubmissionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionInformation
        fields = '__all__'