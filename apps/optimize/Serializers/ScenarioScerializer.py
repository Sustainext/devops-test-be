from ..models.OptimizeScenario import Scenerio
from rest_framework import serializers
from collections import OrderedDict


class ScenerioSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    corporate_name = serializers.CharField(source="corporate.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Scenerio
        fields = "__all__"
        read_only_fields = ["created_by", "updated_by"]

    def get_created_by_name(self, obj):
        if isinstance(obj, dict) or isinstance(obj, OrderedDict):
            # If obj is a dictionary (not a model instance), fetch the data safely
            created_by = obj.get("created_by")
            if created_by and isinstance(created_by, dict):
                first_name = created_by.get("first_name", "")
                last_name = created_by.get("last_name", "")
                return f"{first_name} {last_name}".strip()
            return None

        if obj.created_by:
            first_name = obj.created_by.first_name or ""
            last_name = obj.created_by.last_name or ""
            return f"{first_name} {last_name}".strip()

        return None

    def get_updated_by_name(self, obj):
        if isinstance(obj, dict) or isinstance(obj, OrderedDict):
            # If obj is a dictionary (not a model instance), fetch the data safely
            updated_by = obj.get("updated_by")
            if updated_by and isinstance(updated_by, dict):
                first_name = updated_by.get("first_name", "")
                last_name = updated_by.get("last_name", "")
                return f"{first_name} {last_name}".strip()
            return None
        if obj.updated_by:
            first_name = obj.updated_by.first_name or ""
            last_name = obj.updated_by.last_name or ""
            return f"{first_name} {last_name}".strip()
        return None
