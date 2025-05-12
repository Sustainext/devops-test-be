from rest_framework import serializers
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from sustainapp.models import Corporateentity

class SubmissionInformationSerializer(serializers.ModelSerializer):
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = SubmissionInformation
        fields = '__all__'
