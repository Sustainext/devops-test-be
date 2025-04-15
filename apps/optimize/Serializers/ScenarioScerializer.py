from ..models.OptimizeScenario import Scenerio
from rest_framework import serializers


class ScenerioSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    corporate_name = serializers.CharField(source="corporate.name", read_only=True)

    class Meta:
        model = Scenerio
        fields = "__all__"
        read_only_fields = ["created_by", "updated_by"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["created_by_name"] = instance.created_by.get_full_name()
        data["updated_by_name"] = instance.updated_by.get_full_name()
        return data
