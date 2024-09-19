from sustainapp.models import Corporateentity, Organization
from rest_framework import serializers


class VerifyOrganisationAndCorporateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.none()
    )
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.none(), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request", None)

        if request and hasattr(request.user, "client"):
            client = request.user.client
            self.fields["organization"].queryset = Organization.objects.filter(
                client=client
            )
            self.fields["corporate"].queryset = Corporateentity.objects.filter(
                organization__in=Organization.objects.filter(client=client)
            )
        else:
            self.fields["organization"].queryset = Organization.objects.none()
            self.fields["corporate"].queryset = Corporateentity.objects.none()
