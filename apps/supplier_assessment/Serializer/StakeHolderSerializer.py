from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeHolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeHolder
        fields = "__all__"


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
