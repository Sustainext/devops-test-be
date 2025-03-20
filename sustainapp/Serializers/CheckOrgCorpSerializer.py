from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity


class CheckOrgCoprSerializer(serializers.Serializer):
    """
    Checks if the Organization & Corporate are valid
    """

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=True
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False, allow_null=True
    )

    def validate(self, data):

        org = data.get("organization")
        corp = data.get("corporate")
        if not org:
            raise serializers.ValidationError("Please send a valid organization")

        if corp and corp.organization_id != org.id:
            raise serializers.ValidationError(
                "The given corporate is not liked with the given organization"
            )
        return data