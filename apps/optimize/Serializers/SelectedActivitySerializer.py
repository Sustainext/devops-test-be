from rest_framework import serializers
from ..models.SelectedAvtivityModel import SelectedActivity


class SelectedActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedActivity
        fields = "__all__"
        extra_kwargs = {"scenario": {"read_only": True}}
