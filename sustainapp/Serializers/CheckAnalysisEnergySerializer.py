from serializers import serializers
from sustainapp.models import Organization, Corporateentity, Location


class AnalyzeEnergySerializer(serializers.Serializer):
    """
    AnalyzeEnergySerializer is a serializer for the Emission Analyse API.
    It checks the input for the date, location, corporate entity and organisation.
    """

    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=True)
    corporate = serializers.PrimaryKeyRelatedField(queryset=Corporateentity.objects.all(), required=False)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=False)

    def validate(self, data):

        location = data.get("location")
        corporate = data.get("corporate")
        organization = data.get('organization')

        if location :
            if not organization or not corporate:
                raise serializers.ValidationError("You must provide an organization and a corporate entity")
        elif corporate :
            if not organization:
                raise serializers.ValidationError("You must provide an organization")

        return data