from rest_framework import serializers
from materiality_dashboard.models import MaterialityImpact


class MaterialityImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityImpact
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["material_topic_name"] = instance.material_topic.name
        return data


class MaterialityImpactBulkSerializer(serializers.ListSerializer):
    child = MaterialityImpactSerializer()

    def create(self, validated_data):
        materiality_impacts = [MaterialityImpact(**item) for item in validated_data]
        return MaterialityImpact.objects.bulk_create(materiality_impacts)

    def update(self, instances, validated_data):
        # Create a dictionary mapping instance IDs (or another unique field) to instances
        instance_mapping = {instance.id: instance for instance in instances}

        # Initialize a list for storing the results of the update
        result = []

        # Iterate through validated data
        for attrs in validated_data:
            instance_id = attrs.get("id")  # Added Unique Identifier for Keyerror 1

            if instance_id in instance_mapping:
                instance = instance_mapping.pop(instance_id)
                result.append(self.child.update(instance, attrs))
            else:

                result.append(self.child.create(attrs))

        return result
