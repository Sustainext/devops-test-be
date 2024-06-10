from rest_framework import serializers

class CheckAnalysisViewSerializer(serializers.Serializer):
    """
    CheckAnalysisViewSerializer is a serializer for the Emission Analyse API.
    It checks the input for the year, corporate entity and organisation.
    """

    year = serializers.IntegerField(required=True)
    corporate = serializers.CharField(required=True)
    organisation = serializers.CharField(required=True)

    class Meta:
        fields = ("year", "corporate", "organisation")

    


