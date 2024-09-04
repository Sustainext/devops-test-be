from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import MaterialityAssessmentSerializer
from rest_framework import serializers

class MaterialityAssessmentViewSet(viewsets.ModelViewSet):
    queryset = MaterialityAssessment.objects.all()
    serializer_class = MaterialityAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaterialityAssessment.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        #* Add a validation that checks the time period of the assessment with the framework is not overlapping with any in_progress assessment
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        if MaterialityAssessment.objects.filter(client=self.request.user.client, status="in_progress",start_date__gte=start_date,end_date__lte=end_date,framework=serializer.validated_data["framework"]).exists():
            raise serializers.ValidationError({"error": "Client already has an in progress assessment."})

        serializer.save(client=self.request.user.client)
