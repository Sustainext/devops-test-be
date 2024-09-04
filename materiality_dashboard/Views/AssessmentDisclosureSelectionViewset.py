from rest_framework.views import APIView
from materiality_dashboard.models import AssessmentDisclosureSelection
from materiality_dashboard.Serializers.AssessmentDisclosureSelectionSerializer import (
    BulkAssessmentDisclosureSelectionSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import (
    MaterialityAssessment,
    MaterialTopic,
    Disclosure,
)
from collections import defaultdict
from django.db.models import Prefetch


class AssessmentDisclosureSelectionAPIView(APIView):
    """
    Disclosure Selection for Assessment
    Provides an API view for creating `AssessmentDisclosureSelection` objects.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BulkAssessmentDisclosureSelectionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = {
            "message": "Assessment Disclosure Selection created successfully."
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def get(self, request, assessment_id, *args, **kwargs):
        topic_selection_ids = request.query_params.getlist("topic_selection_ids")

        try:
            disclosures = AssessmentDisclosureSelection.objects.filter(
                topic_selection__id__in=topic_selection_ids,
                topic_selection__assessment__id=assessment_id,
            ).select_related("topic_selection", "disclosure")
        except AssessmentDisclosureSelection.DoesNotExist:
            return Response(
                {
                    "error": "No disclosures found for the given assessment and topic selections."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = [
            {
                "id": disclosure.id,
                "topic_selection_id": disclosure.topic_selection.id,
                "disclosure_id": disclosure.disclosure.id,
                "disclosure_description": disclosure.disclosure.description,
            }
            for disclosure in disclosures
        ]
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, assessment_id, *args, **kwargs):
        serializer = BulkAssessmentDisclosureSelectionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            validated_data = serializer.validated_data["validated_data"]
            for item in validated_data:
                topic_selection = item["topic_selection"]

                # Remove existing disclosure selections for this topic selection
                AssessmentDisclosureSelection.objects.filter(
                    topic_selection=topic_selection
                ).delete()

                # Create new selections based on the provided disclosures
                for disclosure in item["validated_disclosures"]:
                    AssessmentDisclosureSelection.objects.create(
                        topic_selection=topic_selection, disclosure=disclosure
                    )

            return Response({"status": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMaterialTopicDisclosures(APIView):
    """
    Get Material Topic Disclosures
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id, format=None):
        try:
            # Fetch the materiality assessment for the given id
            materiality_assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=self.request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {
                    "error": "No materiality assessment found for the given assessment id."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prefetch disclosures for the selected topics efficiently
        selected_material_topics = materiality_assessment.selected_topics.prefetch_related(
            Prefetch(
                "topic__disclosure_set",  # Accessing disclosures for each topic
                to_attr="prefetched_disclosures",  # Store the result in a prefetched attribute
            )
        ).select_related(
            "topic"
        )

        response_data = defaultdict(list)

        # Iterate over selected material topics and use prefetched disclosures
        for selected_material_topic in selected_material_topics:
            response_data[selected_material_topic.topic.esg_category].append(
                {
                    f"{selected_material_topic.topic.name}": [
                        {
                            "name": disclosure.description,
                            "disclosure_id": disclosure.id,
                            "selected_material_topic_id": selected_material_topic.id,
                            "material_topic_id": selected_material_topic.topic.id,
                        }
                        for disclosure in selected_material_topic.topic.prefetched_disclosures
                    ]
                }
            )

        return Response(response_data, status=status.HTTP_200_OK)
