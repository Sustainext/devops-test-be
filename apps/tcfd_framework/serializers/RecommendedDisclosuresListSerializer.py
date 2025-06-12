from rest_framework import serializers
from apps.tcfd_framework.models.TCFDCollectModels import RecommendedDisclosures
from sustainapp.models import Organization, Corporateentity


class RecommendedDisclosureIdListSerializer(serializers.Serializer):
    """
    Serializer to validate a list of RecommendedDisclosures IDs.
    """

    recommended_disclosures = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=RecommendedDisclosures.objects.all()
        ),
        allow_empty=False,
        help_text="List of RecommendedDisclosures IDs.",
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), help_text="ID of the organization."
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        help_text="ID of the corporate entity.",
        required=False,
        allow_null=True,
    )
