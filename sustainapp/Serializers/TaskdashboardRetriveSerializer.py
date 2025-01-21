from sustainapp.models import ClientTaskDashboard
from rest_framework import serializers
from django.apps import apps
from django.conf import settings
from sustainapp.signals import task_status_changed

# Extracting the User Model
CustomUser = apps.get_model(settings.AUTH_USER_MODEL)


class ClientTaskDashboardSerializer(serializers.ModelSerializer):
    assign_to_email = serializers.CharField(
        source="assigned_to.email", required=False, read_only=True
    )
    assign_to_user_name = serializers.CharField(
        source="assigned_to.first_name", required=False, read_only=True
    )

    assign_by_email = serializers.CharField(
        source="assigned_by.email", required=False, read_only=True
    )
    assign_by_user_name = serializers.CharField(
        source="assigned_by.first_name", required=False, read_only=True
    )
    location_name = serializers.CharField(
        source="location.name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        fields = "__all__"
        read_only_fields = ["assigned_by"]

    # def create(self, validated_data):
    #     # Get the user making the request
    #     user = self.request.user
    #     # Set the assigned_by field to the user making the request
    #     validated_data["assigned_by"] = user
    #     return super().create(validated_data)

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
    assign_to_user_name = serializers.CharField(
        source="assigned_to.first_name", required=False, read_only=True
    )

    class Meta:
        model = ClientTaskDashboard
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "client"]
