from rest_framework import serializers
from materiality_dashboard.models import (
    AssessmentDisclosureSelection,
    Disclosure,
    MaterialityAssessment,
    AssessmentTopicSelection,
)


class AssessmentDisclosureSelectionSerializer(serializers.Serializer):
    """
    Serializer for the AssessmentDisclosureSelection model.
    """

    topic_selections = serializers.PrimaryKeyRelatedField(
        queryset=AssessmentTopicSelection.objects.all(), many=True
    )
    disclosures = serializers.PrimaryKeyRelatedField(
        queryset=Disclosure.objects.all(), many=True
    )
    assessment_id = serializers.IntegerField()

    class Meta:
        model = AssessmentDisclosureSelection
        fields = ["topic_selections", "disclosure", "assessment_id"]

    def validate(self, data):
        topic_selections = data.get("topic_selections")
        disclosures = data.get("disclosures")
        assessment_id = data.get("assessment_id")
        if not topic_selections or not disclosures or not assessment_id:
            raise serializers.ValidationError(
                "Both topic_selections, disclosures and assessment_id are required."
            )
        # Validate the topic_selections
        request = self.context.get("request")
        try:
            # * Getting the assessment instance
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=request.user.client
            )
            # * Getting the assessment topic selections for the assessment
            assessment_topic_selections = AssessmentTopicSelection.objects.filter(
                id__in=topic_selections, assessment=assessment
            ).select_related("topic")
            # * Getting the disclosures for the assessment disclosure selections
            disclosures = Disclosure.objects.filter(
                id__in=disclosures,
                topic__in=assessment_topic_selections.values_list("topic", flat=True),
            )
            if assessment_topic_selections.count() != len(topic_selections):
                raise serializers.ValidationError(
                    "One or more topic_selections do not belong to the specified assessment."
                )
            if not assessment_topic_selections.exists():
                raise serializers.ValidationError(
                    "No topic_selections have been selected."
                )
            if not disclosures.exists():
                raise serializers.ValidationError(
                    "No disclosures have been found for the selected topics or their IDs are invalid."
                )
        except MaterialityAssessment.DoesNotExist:
            raise serializers.ValidationError(
                {"assessment_id": "Materiality Assessment does not exist."}
            )

        # Store validated data
        data["validated_disclosures"] = disclosures
        data["validated_topic_selections"] = assessment_topic_selections

        return data

    def create(self, validated_data):
        disclosures = validated_data["validated_disclosures"]
        topic_selections = validated_data["validated_topic_selections"]

        for selected_topic in topic_selections:
            for disclosure in disclosures:
                if disclosure.topic == selected_topic.topic:
                    selections = [
                        AssessmentDisclosureSelection(
                            topic_selection=selected_topic,
                            disclosure=disclosure,
                        )
                        for disclosure in disclosures
                    ]

        return AssessmentDisclosureSelection.objects.bulk_create(selections)
