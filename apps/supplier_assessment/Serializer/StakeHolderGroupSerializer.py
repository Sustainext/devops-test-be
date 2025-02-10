from rest_framework import serializers
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup


class CheckStakeHolderGroupSerializer(serializers.Serializer):
    """
    Verifies whether the stakeholder group exists.
    """

    group = serializers.PrimaryKeyRelatedField(queryset=StakeHolderGroup.objects.all())

    def validate_group(self, value):
        user = self.context["request"].user
        if value.created_by != user:
            raise serializers.ValidationError(
                "You don't have permission to access this group."
            )
        return value


class StakeHolderGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for StakeHolderGroup model.
    """

    def validate(self, data):
        # First run any existing validation from parent class
        data = super().validate(data)

        user = self.context["request"].user

        if "organization" in data and data["organization"] not in user.orgs.all():
            raise serializers.ValidationError(
                "You don't have permission for this organization"
            )

        if "corporate" in data and data["corporate"] not in user.corps.all():
            raise serializers.ValidationError(
                "You don't have permission for this corporate"
            )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["organization_name"] = instance.organization.name
        # * Get all corporates names from the instance
        data["corporate_names"] = [
            corporate.name for corporate in instance.corporate_entity.all()
        ]
        return data

    class Meta:
        model = StakeHolderGroup
        fields = "__all__"
        read_only_fields = ("created_by",)
