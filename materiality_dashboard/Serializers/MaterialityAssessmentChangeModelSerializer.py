from rest_framework import serializers
from materiality_dashboard.models import MaterialityChangeConfirmation


class MaterialityChangeConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityChangeConfirmation
        fields = "__all__"
