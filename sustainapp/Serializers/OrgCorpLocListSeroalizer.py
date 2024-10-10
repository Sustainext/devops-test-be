# serializers.py
from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity, Location


class LocationSerializer(serializers.ModelSerializer):
    corporate_name = serializers.CharField(source="corporateentity.name")

    class Meta:
        model = Location
        fields = ["id", "name", "corporate_name"]


class CorporateSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Corporateentity
        fields = [
            "id",
            "name",
            "organization_name",
        ]
