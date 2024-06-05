from rest_framework import serializers
from .models import FieldGroup, RawResponse


class FieldGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldGroup
        fields = ["id", "name", "meta_data", "ui_schema", "schema", "path"]


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
    client_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    # schema = serializers.JSONField(required=False)
    # Add more fields as needed

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
