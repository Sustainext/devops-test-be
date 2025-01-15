from dj_rest_auth.serializers import PasswordResetConfirmSerializer
from django.contrib.auth.hashers import check_password
from rest_framework import serializers


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        user = self.user
        new_password = attrs.get("new_password1")

        if user.old_password and check_password(new_password, user.old_password):
            raise serializers.ValidationError(
                "Your new password cannot be the same as your previous password."
            )
        return attrs
