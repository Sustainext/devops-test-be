from rest_framework.views import APIView
from materiality_dashboard.models import AssessmentDisclosureSelection
from materiality_dashboard.Serializers.AssessmentDisclosureSelectionSerializer import (
    BulkAssessmentDisclosureSelectionSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import MaterialityAssessment
from collections import defaultdict


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
