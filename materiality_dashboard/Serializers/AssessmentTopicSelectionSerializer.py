from rest_framework import serializers
from materiality_dashboard.models import (
    MaterialityAssessment,
    MaterialTopic,
    AssessmentTopicSelection,
)
from rest_framework.response import Response
from rest_framework import status


class AssessmentTopicSelectionSerializer(serializers.Serializer):
    assessment_id = serializers.IntegerField()
    topics = serializers.PrimaryKeyRelatedField(
        queryset=MaterialTopic.objects.all(), many=True
    )

    def validate(self, data):
        assessment_id = data.get("assessment_id")
        topics = data.get("topics")

        # Validate the assessment_id
        try:
            assessment = MaterialityAssessment.objects.get(id=assessment_id)
        except MaterialityAssessment.DoesNotExist:
            raise serializers.ValidationError(
                {"assessment_id": "Materiality Assessment does not exist."}
            )

        # Store validated data
        data["assessment"] = assessment
        data["validated_topics"] = topics

        return data

    def create(self, validated_data):
        assessment = validated_data["assessment"]
        topics = validated_data["validated_topics"]

        selections = [
            AssessmentTopicSelection(assessment=assessment, topic=topic)
            for topic in topics
        ]

        return AssessmentTopicSelection.objects.bulk_create(selections)
