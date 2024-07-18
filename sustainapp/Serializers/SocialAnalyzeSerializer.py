from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity, Location


class SocialAnalysisSerializer(serializers.Serializer):
    """
    CheckAnalysisViewSerializer is a serializer for the Emission Analyse API.
    It checks the input for the year, corporate entity and organisation.
    """

    year = serializers.IntegerField(min_value=1980)
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=False
    )

    def validate(self, data):
        if not any(
            [data.get("organization"), data.get("corporate")]
        ):
            raise serializers.ValidationError(
                "At least one of 'organisation', or 'corporate' is required."
            )
        return data

    class Meta:
        fields = ("year", "corporate", "organization")
