from rest_framework import serializers
from sustainapp.models import Corporateentity, Organization

class CheckYearOrganizationCorporateSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        required=False,
        allow_null=True
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
    )
    # Meta class is not used by serializers.Serializer for field listing
    # class Meta:
    #     fields = ["year", "organization", "corporate"]
