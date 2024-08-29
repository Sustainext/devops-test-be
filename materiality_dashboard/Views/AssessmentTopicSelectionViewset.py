from rest_framework.views import APIView
from materiality_dashboard.models import AssessmentTopicSelection
from materiality_dashboard.Serializers.AssessmentTopicSelectionSerializer import (
    AssessmentTopicSelectionSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import MaterialityAssessment


class AssessmentTopicSelectionAPIView(APIView):
    """
    Topic Selection for Assessment
    Provides an API view for creating `AssessmentTopicSelection` objects.

    This view allows authenticated users to create one or more `AssessmentTopicSelection`
    objects, which represent the topics selected for a particular assessment.

    The view expects a list of topic IDs in the request data, and returns a list of
    the created `AssessmentTopicSelection` objects, including their IDs, the assessment
    ID, and the topic name.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AssessmentTopicSelectionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        created_selections = AssessmentTopicSelection.objects.filter(
            assessment__id=serializer.validated_data["assessment_id"]
        ).select_related("topic")
        response_data = [
            {
                "id": selection.id,
                "assessment_id": selection.assessment.id,
                "topic_name": selection.topic.name,
            }
            for selection in created_selections
        ]
        return Response(response_data, status=status.HTTP_201_CREATED)

    def put(self, request, assessment_id, *args, **kwargs):
        # Retrieve the assessment instance
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=self.request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {"error": "Materiality Assessment does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate the input data
        serializer = AssessmentTopicSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Remove existing topic selections for this assessment
        AssessmentTopicSelection.objects.filter(assessment=assessment).delete()
        # Create new selections based on the provided topics
        serializer.save()
        created_selections = AssessmentTopicSelection.objects.filter(
            assessment=assessment
        ).select_related("topic")
        response_data = [
            {
                "id": selection.id,
                "assessment_id": selection.assessment.id,
                "topic_name": selection.topic.name,
            }
            for selection in created_selections
        ]
        return Response(response_data, status=status.HTTP_200_OK)
