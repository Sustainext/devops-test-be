from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeHolderSerializer(serializers.ModelSerializer):
    latest_name = serializers.CharField(read_only=True)
    latest_email = serializers.CharField(read_only=True)
    oldest_name = serializers.CharField(read_only=True)
    oldest_email = serializers.CharField(read_only=True)

    class Meta:
        model = StakeHolder
        fields = [
            "id",
            "name",
            "group",
            "email",
            "address",
            "country",
            "city",
            "state",
            "latitude",
            "longitude",
            "poc",
            "created_at",
            "updated_at",
            "latest_name",
            "latest_email",
            "oldest_name",
            "oldest_email",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        return data


# * A serializer that checks for .csv files
class StakeHolderCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField()

    def validate_csv_file(self, value):
        if not value.name.endswith(".csv"):
            raise serializers.ValidationError("Uploaded file is not a CSV.")

        # Check if file is empty
        if value.size == 0:
            raise serializers.ValidationError("The uploaded file is empty")

        return value


# * A serializer for accepts IDs of Stakeholder Models
class DeleteIDsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of IDs to delete.",
    )
