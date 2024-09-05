from rest_framework import serializers
from materiality_dashboard.models import MaterialityImpact

class MaterialityImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityImpact
        fields = "__all__"


class MaterialityImpactBulkSerializer(serializers.ListSerializer):
    child = MaterialityImpactSerializer()

    def create(self, validated_data):
        materiality_impacts = [MaterialityImpact(**item) for item in validated_data]
        return MaterialityImpact.objects.bulk_create(materiality_impacts)

    def update(self, instances, validated_data):
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [
            self.child.update(instance_hash[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]

        return result
