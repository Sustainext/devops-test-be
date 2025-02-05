from sustainapp.models import ClientTaskDashboard
from rest_framework import serializers
from django.apps import apps
from django.conf import settings
from sustainapp.signals import task_status_changed
from rest_framework.exceptions import ValidationError

# Extracting the User Model
CustomUser = apps.get_model(settings.AUTH_USER_MODEL)


class ClientTaskDashboardSerializer(serializers.ModelSerializer):
    assign_to_email = serializers.CharField(
        source="assigned_to.email", required=False, read_only=True
    )
    assign_to_user_name = serializers.SerializerMethodField()

    assign_by_email = serializers.CharField(
        source="assigned_by.email", required=False, read_only=True
    )
    assign_by_user_name = serializers.SerializerMethodField()
    location_name = serializers.CharField(
        source="location.name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        fields = "__all__"
        read_only_fields = ["assigned_by"]

    def get_assign_to_user_name(self, obj):
        if obj.assigned_to:
            first_name = obj.assigned_to.first_name or ""
            last_name = obj.assigned_to.last_name or ""
            return f"{first_name} {last_name}".strip()
        return None

    def get_assign_by_user_name(self, obj):
        if obj.assigned_by:
            first_name = obj.assigned_by.first_name or ""
            last_name = obj.assigned_by.last_name or ""
            return f"{first_name} {last_name}".strip()
        return None

    def update(self, instance, validated_data):
        comments = self.context["request"].data.get(
            "comments", ""
        )  # Assuming comments are sent in the request
        instance = super().update(instance, validated_data)

        # Emit the custom signal after the instance is saved
        task_status_changed.send(
            sender=instance.__class__, instance=instance, comments=comments
        )
        return instance


class TaskDashboardCustomSerializer(serializers.ModelSerializer):
    assign_to_email = serializers.CharField(
        source="assigned_to.email", required=False, read_only=True
    )
    assign_to_user_name = serializers.SerializerMethodField()
    assign_by_email = serializers.CharField(
        source="assigned_by.email", required=False, read_only=True
    )
    assign_by_user_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source="location.corporateentity.organization.name",
        required=False,
        read_only=True,
    )
    corporate_name = serializers.CharField(
        source="location.corporateentity.name", required=False, read_only=True
    )
    location_name = serializers.CharField(
        source="location.name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        fields = "__all__"

    def get_assign_to_user_name(self, obj):
        if obj.assigned_to:
            first_name = obj.assigned_to.first_name or ""
            last_name = obj.assigned_to.last_name or ""
            return f"{first_name} {last_name}".strip()
        return None

    def get_assign_by_user_name(self, obj):
        if obj.assigned_by:
            first_name = obj.assigned_by.first_name or ""
            last_name = obj.assigned_by.last_name or ""
            return f"{first_name} {last_name}".strip()
        return None


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "client"]


class ClientTaskDashboardBulkUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = ClientTaskDashboard
        fields = "__all__"
        read_only_fields = ["assigned_by"]

    def validate_assigned_to(self, value):
        """Ensure assigned_to is a valid CustomUser instance."""
        if value and not isinstance(value, CustomUser):
            try:
                return CustomUser.objects.get(id=value)
            except CustomUser.DoesNotExist:
                raise ValidationError("User with the given ID does not exist.")
        return value
