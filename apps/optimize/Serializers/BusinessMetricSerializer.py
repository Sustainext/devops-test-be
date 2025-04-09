from ..models.BusinessMetric import BusinessMetric
from rest_framework import serializers


class BusinessMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMetric
        fields = "__all__"
