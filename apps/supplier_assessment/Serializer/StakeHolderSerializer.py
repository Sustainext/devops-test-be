from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeHolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeHolder
        fields = "__all__"