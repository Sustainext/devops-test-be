from rest_framework import serializers
from sustainapp.models import MyGoalOrganization


class MyGoalsOrganizationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.first_name", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = MyGoalOrganization
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "client",
        )
