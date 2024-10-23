from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from authentication.models import CustomRole

CustomUser = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    orgs = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    corps = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    locs = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    custom_role = serializers.SlugRelatedField(
        slug_field="name",
        queryset=CustomRole.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "job_title",
            "department",
            "work_email",
            "client",
            "custom_role",
            "orgs",
            "corps",
            "locs",
            "collect",
            "analyse",
            "report",
            "optimise",
            "track",
        ]
        extra_kwargs = {
            "client": {"read_only": True},
            "username": {"required": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "job_title": {"required": True},
            "department": {"required": True},
            "work_email": {"required": True},
            "collect": {"required": True},
            "analyse": {"required": True},
            "report": {"required": True},
            "optimise": {"required": True},
            "track": {"required": True},
        }

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        if data.get("email") != data.get("work_email"):
            raise serializers.ValidationError("Email and work email must be the same.")
        return data

    @transaction.atomic
    def create(self, validated_data):
        org_list = validated_data.pop("orgs", [])
        corp_list = validated_data.pop("corps", [])
        loc_list = validated_data.pop("locs", [])

        try:
            # Create a new user instance
            user = CustomUser.objects.create_user(**validated_data)

            # Set the related fields
            user.orgs.set(org_list)
            user.corps.set(corp_list)
            user.locs.set(loc_list)

            return user
        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            # and the user will not be created
            raise serializers.ValidationError(f"Error creating user: {str(e)}")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["orgs"] = list(instance.orgs.values_list("id", flat=True))
        ret["corps"] = list(instance.corps.values_list("id", flat=True))
        ret["locs"] = list(instance.locs.values_list("id", flat=True))
        return ret
