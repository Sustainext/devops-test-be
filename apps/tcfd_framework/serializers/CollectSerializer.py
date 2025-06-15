from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity, Location

class CollectBasicSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all()
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        required=False,
        allow_null=True
    )
    year=serializers.IntegerField()

    