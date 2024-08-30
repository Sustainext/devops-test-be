from rest_framework import serializers
from materiality_dashboard.models import (
    AssessmentDisclosureSelection,
    MaterialityAssessment,
    AssessmentTopicSelection,
    Disclosure,
)


class BulkAssessmentDisclosureSelectionSerializer(serializers.Serializer):
    assessment_id = serializers.IntegerField()
    topic_disclosures = serializers.ListField(
        child=serializers.DictField(
            child=serializers.ListField(child=serializers.IntegerField())
        )
    )

    def validate(self, data):
        assessment_id = data.get("assessment_id")
        topic_disclosures = data.get("topic_disclosures")
        request = self.context.get("request")
        # Validate the assessment_id
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            raise serializers.ValidationError(
                {"assessment_id": "Materiality Assessment does not exist."}
            )

        validated_data = []
        for topic_disclosure in topic_disclosures:
            topic_selection_ids = topic_disclosure.get("topic_selection_id")
            disclosure_ids = topic_disclosure.get("disclosure_ids")

            if len(topic_selection_ids) != 1:
                raise serializers.ValidationError(
                    {
                        "topic_selection_ids": "Only one topic_selection_id is allowed in each entry."
                    }
                )

            # Extract the single topic_selection_id
            topic_selection_id = topic_selection_ids[0]
            # Validate the topic selection
            try:
                topic_selection = AssessmentTopicSelection.objects.get(
                    id=topic_selection_id, assessment=assessment
                )
            except AssessmentTopicSelection.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "topic_selection_id": f"Topic selection {topic_selection_id} does not exist or does not belong to the specified assessment."
                    }
                )

            # Validate each disclosure ID
            validated_disclosures = []
            disclosure = Disclosure.objects.filter(id__in=disclosure_ids)
            # * Check if every disclosure exists
            if len(disclosure) != len(disclosure_ids):
                not_present_disclosure_ids = set(disclosure_ids) - set(
                    disclosure.values_list("id", flat=True)
                )
                raise serializers.ValidationError(
                    "Disclosure(s) not present: "
                    + ", ".join(map(str, not_present_disclosure_ids))
                )

            validated_data.append(
                {
                    "topic_selection": topic_selection,
                    "validated_disclosures": disclosure,
                }
            )

        data["validated_data"] = validated_data
        return data

    def create(self, validated_data):
        validated_data = validated_data["validated_data"]
        created_selections = []

        for item in validated_data:
            topic_selection = item["topic_selection"]
            disclosures = item["validated_disclosures"]
            for disclosure in disclosures:
                selections = AssessmentDisclosureSelection.objects.create(
                    topic_selection=topic_selection, disclosure=disclosure
                )
                created_selections.append(selections)
                selections.save()
        return created_selections
