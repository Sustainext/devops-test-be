from rest_framework import serializers
from apps.optimize.models.SelectedActivityModel import SelectedActivity
from apps.optimize.utils import RoundedDecimalField


class SelectedActivitySerializer(serializers.ModelSerializer):
    quantity = RoundedDecimalField(max_digits=64, decimal_places=8, required=False)
    quantity2 = RoundedDecimalField(
        max_digits=64, decimal_places=8, required=False, allow_null=True
    )
    co2e_total = RoundedDecimalField(max_digits=64, decimal_places=8, required=False)

    class Meta:
        model = SelectedActivity
        fields = "__all__"
        extra_kwargs = {"scenario": {"read_only": True}}
