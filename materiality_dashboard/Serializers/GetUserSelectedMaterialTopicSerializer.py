from rest_framework import serializers
from materiality_dashboard.models import AssessmentTopicSelection, MaterialTopic


class MaterialTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialTopic
        fields = ["id", "name", "esg_category"]


class AssessmentTopicSelectionSerializer(serializers.ModelSerializer):
    topic = MaterialTopicSerializer()

    class Meta:
        model = AssessmentTopicSelection
        fields = ["id", "topic"]
