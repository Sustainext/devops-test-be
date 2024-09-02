from rest_framework import serializers
from materiality_dashboard.models import MaterialityImpact


class MaterialityImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityImpact
        fields = "__all__"
