from rest_framework import serializers
from sustainapp.models import Corporateentity


class UserSpecificPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request", None)
        user = request.user if request else None
        if user is not None:
            return Corporateentity.objects.filter(client=user.client)
        return Corporateentity.objects.none()


class GetCorporateSerializer(serializers.Serializer):
    corporate = UserSpecificPrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=True
    )

    class Meta:
        fields = ("corporate",)
