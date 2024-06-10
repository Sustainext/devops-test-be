from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity


class CheckAnalysisViewSerializer(serializers.Serializer):
    """
    CheckAnalysisViewSerializer is a serializer for the Emission Analyse API.
    It checks the input for the year, corporate entity and organisation.
    """

    year = serializers.IntegerField(required=True)
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=True
    )
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=True
    )

    class Meta:
        fields = ("year", "corporate", "organisation")
