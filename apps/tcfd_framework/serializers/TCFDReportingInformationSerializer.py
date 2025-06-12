from rest_framework import serializers
from apps.tcfd_framework.models.TCFDReportingModels import TCFDReportingInformation
from sustainapp.models import Corporateentity, Organization


class TCFDReportingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCFDReportingInformation
        fields = "__all__"
        read_only_fields = ("client",)

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request.user, "client"):
            validated_data["client"] = request.user.client
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and hasattr(request.user, "client"):
            validated_data["client"] = request.user.client
        return super().update(instance, validated_data)


class TCFDReportingInformationBasicSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        help_text="The organization for which TCFD reporting information is being provided.",
        error_messages={
            "required": "Organization is required.",
            "does_not_exist": "The specified organization does not exist.",
        },
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        required=False,
        allow_null=True,
        help_text="The corporate entity associated with the organization.",
        error_messages={
            "does_not_exist": "The specified corporate entity does not exist.",
        },
    )
