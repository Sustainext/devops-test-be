from rest_framework.views import APIView
from materiality_dashboard.models import AssessmentDisclosureSelection
from materiality_dashboard.Serializers.AssessmentDisclosureSelectionSerializer import (
    AssessmentDisclosureSelectionSerializer,
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
        serializer = AssessmentDisclosureSelectionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        topic_selection = serializer.validated_data["topic_selection"]
        created_selections = AssessmentDisclosureSelection.objects.filter(
            topic_selection=topic_selection
        ).select_related("disclosure")
        response_data = defaultdict(list)
        for selection in created_selections:
            response_data[selection.disclosure.topic.esg_category].append(
                {
                    "id": selection.id,
                    "assessment_id": selection.topic_selection.assessment.id,
                    "disclosure_name": selection.disclosure.description,
                    "disclosure_topic": selection.disclosure.topic.name,
                }
            )
        return Response(response_data, status=status.HTTP_201_CREATED)
