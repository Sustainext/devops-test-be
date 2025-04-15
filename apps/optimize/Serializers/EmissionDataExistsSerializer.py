from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity


class EmissionDataRequestSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=True
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    year = serializers.IntegerField(required=True)
