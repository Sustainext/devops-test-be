from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import MaterialityAssessmentSerializer


class MaterialityAssessmentViewSet(viewsets.ModelViewSet):
    queryset = MaterialityAssessment.objects.all()
    serializer_class = MaterialityAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaterialityAssessment.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)
