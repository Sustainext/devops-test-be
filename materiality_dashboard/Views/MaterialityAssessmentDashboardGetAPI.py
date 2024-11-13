from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import MaterialityAssessment, Client
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import (
    MaterialityAssessmentGetSerializer,
)
from rest_framework.permissions import IsAuthenticated


class MaterialityAssessmentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Validate client existence
        client = self.request.user.client

        # Filter assessments by client
        assessments = MaterialityAssessment.objects.filter(client=client)

        # Serialize the data
        serializer = MaterialityAssessmentGetSerializer(assessments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
