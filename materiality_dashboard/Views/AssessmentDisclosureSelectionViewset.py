from rest_framework.views import APIView
from materiality_dashboard.models import (
    AssessmentDisclosureSelection,
    AssessmentTopicSelection,
)
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


class AssessmentDisclosureSelectionCreate(APIView):
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
                            "can_edit": disclosure.category
                            != "topic_management_dislcosure",
                        }
                        for disclosure in selected_material_topic.topic.prefetched_disclosures
                    ]
                }
            )

        return Response(response_data, status=status.HTTP_200_OK)


class AssessmentDisclosureSelectionRetrieve(APIView):
    """
    Disclosure Selection for Assessment
    Provides an API view for creating `AssessmentDisclosureSelection` objects.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id, *args, **kwargs):
        # * Get Assessment Object
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=self.request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {"error": "Materiality Assessment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # * Get all topic selection IDs
        topic_selections = AssessmentTopicSelection.objects.filter(
            assessment=assessment
        ).select_related("topic")
        # * Get all topic_management_dislcosure disclosures from all topics
        topic_selection_ids = topic_selections.values_list("id", flat=True)
        selected_disclosures = AssessmentDisclosureSelection.objects.filter(
            topic_selection__id__in=topic_selection_ids
        ).select_related("topic_selection", "disclosure")
        response_data = []
        for assessment_disclosure in selected_disclosures:
            response_data.append(
                {
                    "topic_selection_id": assessment_disclosure.topic_selection.id,
                    "disclosure_id": assessment_disclosure.disclosure.id,
                    "disclosure_description": assessment_disclosure.disclosure.description,
                    "can_edit": assessment_disclosure.disclosure.category
                    != "topic_management_dislcosure",
                }
            )
        #* Requirement by the frontend.
        for topic_selection in topic_selections:
            for disclosure in topic_selection.topic.disclosure_set.filter(
                category="topic_management_dislcosure"
            ):
                response_data.append(
                    {
                        "topic_selection_id": topic_selection.id,
                        "disclosure_id": disclosure.id,
                        "disclosure_description": disclosure.description,
                        "can_edit": False,
                    }
                )
        return Response(response_data, status=status.HTTP_200_OK)


class AssessmentDisclosureSelectionUpdate(APIView):
    """
    Edit Disclosure Selection for Assessment
    Provides an API view for Editing `AssessmentDisclosureSelection` objects.
    """

    def put(self, request, assessment_id, *args, **kwargs):
        serializer = BulkAssessmentDisclosureSelectionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # Using bulk delete and create to optimize DB operations
            validated_data = serializer.validated_data["validated_data"]
            topic_selection_ids = [item["topic_selection"] for item in validated_data]

            # Bulk delete old disclosures
            AssessmentDisclosureSelection.objects.filter(
                topic_selection__in=topic_selection_ids
            ).delete()

            # Bulk create new disclosures
            new_disclosure_selections = [
                AssessmentDisclosureSelection(
                    topic_selection=item["topic_selection"], disclosure=disclosure
                )
                for item in validated_data
                for disclosure in item["validated_disclosures"]
            ]
            AssessmentDisclosureSelection.objects.bulk_create(new_disclosure_selections)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
