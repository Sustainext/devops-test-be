from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = ["password1", "password2"]
