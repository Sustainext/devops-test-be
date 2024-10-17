from sustainapp.models import ClientTaskDashboard
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.apps import apps
from django.conf import settings

# Extracting the User Model
CustomUser = apps.get_model(settings.AUTH_USER_MODEL)


class ClientTaskDashboardSerializer(serializers.ModelSerializer):
    assign_to_email = serializers.CharField(source="assigned_to.email", required=False)
    assign_to_user_name = serializers.CharField(
        source="assigned_to.first_name", required=False, read_only=True
    )

    assign_by_email = serializers.CharField(
        source="assigned_by.email", required=False, read_only=True
    )
    assign_by_user_name = serializers.CharField(
        source="assigned_by.first_name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        exclude = ["created_at", "updated_at"]

    def validate_assigned_to(self, value):
        """
        Validates the `assigned_to` field in the `ClientTaskDashboardSerializer`.
        Ensures that the `assigned_to` and `assigned_by` users belong to the same client.
        Raises a `ValidationError` if the `assigned_to` user does not exist or
        if the users do not belong to the same client.
        """
        if isinstance(self.initial_data, list):
            # If we are processing a bulk request
            for task_data in self.initial_data:
                assigned_to_user_payload = task_data.get("assigned_to")
                assigned_by_user_payload = self.context["request"].user.id

                try:
                    assigned_to_user = CustomUser.objects.get(
                        id=assigned_to_user_payload
                    )
                    assigned_by_user = CustomUser.objects.get(
                        id=assigned_by_user_payload
                    )
                except CustomUser.DoesNotExist:
                    raise ValidationError("Assigned to user does not exist")

                if assigned_to_user.client_id != assigned_by_user.client_id:
                    raise ValidationError(
                        "The assigned_to and assigned_by users must belong to the same client"
                    )
        else:
            # Handle the case for a single task
            assigned_to_user_payload = self.initial_data.get("assigned_to")
            assigned_by_user_payload = self.context["request"].user.id

            try:
                assigned_to_user = CustomUser.objects.get(id=assigned_to_user_payload)
                assigned_by_user = CustomUser.objects.get(id=assigned_by_user_payload)
            except CustomUser.DoesNotExist:
                raise ValidationError("Assigned to user does not exist")

            if assigned_to_user.client_id != assigned_by_user.client_id:
                raise ValidationError(
                    "The assigned_to and assigned_by users must belong to the same client"
                )

        return value


class TaskDashboardCustomSerializer(serializers.ModelSerializer):
    assign_to_email = serializers.CharField(
        source="assigned_to.email", required=False, read_only=True
    )
    assign_to_user_name = serializers.CharField(
        source="assigned_to.first_name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        exclude = ["created_at", "updated_at"]


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "client"]
