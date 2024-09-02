from rest_framework.generics import ListAPIView
from materiality_dashboard.models import AssessmentTopicSelection, MaterialityAssessment
from materiality_dashboard.Serializers.GetUserSelectedMaterialTopicSerializer import (
    AssessmentTopicSelectionSerializer,
)
from rest_framework.permissions import IsAuthenticated


class SelectedMaterialTopicsAPIView(ListAPIView):
    serializer_class = AssessmentTopicSelectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        client = self.request.user.client
        assessment_id = self.kwargs["assessment_id"]
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=client
            )
        except MaterialityAssessment.DoesNotExist:
            return AssessmentTopicSelection.objects.none()
        return AssessmentTopicSelection.objects.filter(assessment=assessment)
