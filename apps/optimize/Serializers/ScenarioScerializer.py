from ..models.OptimizeScenario import Scenerio
from rest_framework import serializers


class ScenerioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenerio
        fields = "__all__"
        read_only_fields = ["created_by", "updated_by"]
