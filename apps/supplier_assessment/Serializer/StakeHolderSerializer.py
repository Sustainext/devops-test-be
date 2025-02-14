from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeHolderSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True)
    last_updated_by = serializers.CharField(read_only=True)

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
            "created_by",
            "last_updated_by",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
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
