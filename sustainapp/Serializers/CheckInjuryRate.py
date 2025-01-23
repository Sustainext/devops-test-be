from rest_framework import serializers


class CheckInjuryRateSerializer(serializers.Serializer):
    """
    CheckInjuryRateSerializer is a serializer for the OHS Analyse API.
    It checks for the base of calculating the injury rate.
    """

    injury_rate = serializers.ChoiceField(required=True, choices=[100, 500])

    class Meta:
        fields = ["injury_rate"]
