from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import (
    MaterialityAssessmentProcess,
    MaterialityAssessment,
)
from materiality_dashboard.Serializers.MaterialityAssessmentProcessSerializer import (
    MaterialityAssessmentProcessSerializer,
)


class MaterialityAssessmentProcessCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MaterialityAssessmentProcessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialityAssessmentProcessDetailAPIView(APIView):
    def get_object(self, assessment_id):
        try:
            return MaterialityAssessmentProcess.objects.get(
                assessment__id=assessment_id
            )
        except MaterialityAssessmentProcess.DoesNotExist:
            return None

    def get(self, request, assessment_id, *args, **kwargs):
        assessment_process = self.get_object(assessment_id)
        if assessment_process is None:
            return Response(
                {"error": "Materiality Assessment Process not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MaterialityAssessmentProcessSerializer(assessment_process)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, assessment_id, *args, **kwargs):
        assessment_process = self.get_object(assessment_id)
        if assessment_process is None:
            return Response(
                {"error": "Materiality Assessment Process not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MaterialityAssessmentProcessSerializer(
            assessment_process, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
