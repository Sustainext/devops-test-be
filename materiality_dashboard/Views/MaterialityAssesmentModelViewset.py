from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import MaterialityAssessmentSerializer
from rest_framework import serializers
from  rest_framework.response import Response
from rest_framework import status
from datetime import datetime

class MaterialityAssessmentViewSet(viewsets.ModelViewSet):
    queryset = MaterialityAssessment.objects.all()
    serializer_class = MaterialityAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaterialityAssessment.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)
    
    def create(self, request, *args, **kwargs):
        organization = request.data.get('organization')
        corporate = request.data.get('corporate',None)
        approach = request.data.get('approach')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        if corporate:
            existing_assessments = MaterialityAssessment.objects.filter(
                corporate = corporate,
                approach=approach,
                client=request.user.client
            )
        else:        
            existing_assessments = MaterialityAssessment.objects.filter(
                organization=organization,
                corporate__isnull=True,
                approach=approach,
                client=request.user.client
            )

        for assessment in existing_assessments:
            if start_date > assessment.end_date:
                assessment.status = 'outdated'
                assessment.save()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
