from rest_framework import serializers
from esg_report.models.ScreenOne import CeoMessage


class CeoMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the CEO Message model
    """

    class Meta:
        model = CeoMessage
        fields = "__all__"
