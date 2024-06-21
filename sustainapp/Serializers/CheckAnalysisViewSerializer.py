from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity, Location


class CheckAnalysisViewSerializer(serializers.Serializer):
    """
    CheckAnalysisViewSerializer is a serializer for the Emission Analyse API.
    It checks the input for the year, corporate entity and organisation.
    """

    year = serializers.IntegerField(required=True)
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=False
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), required=False
    )

    def validate(self, data):
        if not any(
            [data.get("location"), data.get("organisation"), data.get("corporate")]
        ):
            raise serializers.ValidationError(
                "At least one of 'location', 'organisation', or 'corporate' is required."
            )
        return data

    class Meta:
        fields = ("year", "corporate", "organisation")
