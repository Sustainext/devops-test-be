from rest_framework import serializers
from authentication.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")
    designation = serializers.ReadOnlyField(source="user.job_title")
    department = serializers.ReadOnlyField(source="user.department")
    user_id = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "designation",
            "designation",
            "department",
            "phone",
            "profile_picture",
            "user_id",
        )
