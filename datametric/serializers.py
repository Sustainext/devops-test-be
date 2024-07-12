from rest_framework import serializers
from .models import FieldGroup, RawResponse
from sustainapp.models import Organization, Corporateentity, Location

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
    # location = serializers.CharField(required=True, trim_whitespace=False)
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), required=False
    )
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=False
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=False)
    def validate(self, data):
        if not any(
            [data.get("location"), data.get("organisation"), data.get("corporate")]
        ):
            raise serializers.ValidationError(
                "At least one of 'location', 'organisation', or 'corporate' is required."
            )
        if data.get("month"):
            if data.get("month") < 1 or data.get("month") > 12:
                raise serializers.ValidationError(
                    "The'month' must be between 1 and 12."
                )
        return data


class RawResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawResponse
        fields = ["id", "data", "updated_at"]


class FieldGroupGetSerializer(serializers.Serializer):
    path_slug = serializers.CharField(required=True)
    # location = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=False)
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=False
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), required=False
    )

    class Meta:
        fields = ["path_slug", "year", "month", "organisation", "corporate"]

    def validate(self, data):

        if not any(
            [data.get("location"), data.get("organisation"), data.get("corporate")]
        ):
            raise serializers.ValidationError(
                "At least one of 'location', 'organisation', or 'corporate' is required."
            )

        # Check for this logic that month can be null also
        if data.get("month"):
            if data.get("month") < 1 or data.get("month") > 12:
                raise serializers.ValidationError(
                    "The'month' must be between 1 and 12."
                )

        return data



class GetClimatiqComputedSerializer(serializers.Serializer):
    # location = serializers.CharField(required=True)
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), required=True
    )
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=True)

    class Meta:
        fields = ["location", "year", "month"]
