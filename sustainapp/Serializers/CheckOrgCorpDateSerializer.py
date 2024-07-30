from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity


class CheckOrgCoprDateSerializer(serializers.Serializer):
    """
    Checks if the Organization, Corporate and selected date range are valid
    """

    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=True
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False, allow_null=True
    )
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=True)

    def validate(self, data):

        org = data.get("organisation")
        corp = data.get("corporate")
        if not org:
            raise serializers.ValidationError("Please send a valid organisation")

        if corp and corp.organization_id != org.id:
            raise serializers.ValidationError(
                "The given corporate is not liked with the given organization"
            )
        if data.get("start") > data.get("end"):
            raise serializers.ValidationError(
                "The 'from_date' must be before the 'to_date'."
            )
        return data
