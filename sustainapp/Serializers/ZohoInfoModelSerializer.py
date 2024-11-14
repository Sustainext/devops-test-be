from sustainapp.models import ZohoInfo
from rest_framework import serializers
from sustainapp.models import Client


class ZohoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZohoInfo
        fields = "__all__"

    def validate_client(self, value):
        if (
            not value
            and self.context["request"].user.client != value
            and Client.objects.filter(id=value).exists()
        ):
            raise serializers.ValidationError(
                "Client does not match authenticated user's client"
            )
        return value
