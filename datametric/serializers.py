from rest_framework import serializers
from .models import FieldGroup, RawResponse


class FieldGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldGroup
        fields = "__all__"


class UpdateResponseSerializer(serializers.Serializer):
    path = serializers.CharField(required=True)
    response_json = serializers.ListField(
        child=serializers.JSONField(), allow_empty=True
    )
    # Add more fields as needed

    def validate(self, data):
        """
        Perform custom validation for the fields.
        """
        # Add custom validation logic here
        return data


class UpdateResponseSerializer(serializers.Serializer):
    path = serializers.CharField(required=True)
    form_data = serializers.ListField(child=serializers.JSONField(), allow_empty=True)
    location = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=True)
    def validate(self, data):
        """
        Perform custom validation for the fields.
        """
        # Add custom validation logic here
        return data


class RawResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawResponse
        fields = ["id", "data", "updated_at"]

class FieldGroupGetSerializer(serializers.Serializer):
    path_slug = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=True)
    class Meta:
        fields = ["path_slug", "location", "year", "month"]
