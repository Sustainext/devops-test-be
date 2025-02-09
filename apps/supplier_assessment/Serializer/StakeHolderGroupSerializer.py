from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup


class CheckStakeHolderGroupSerializer(serializers.Serializer):
    """
    Verifies whether the stakeholder group exists.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=StakeHolderGroup.objects.all())
