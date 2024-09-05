from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import (
    MaterialityChangeConfirmation,
    MaterialityAssessment,
)
from materiality_dashboard.Serializers.MaterialityAssessmentChangeModelSerializer import (
    MaterialityChangeConfirmationSerializer,
)
from rest_framework.permissions import IsAuthenticated


class MaterialityChangeConfirmationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MaterialityChangeConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialityChangeConfirmationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, assessment_id):
        try:
            return MaterialityChangeConfirmation.objects.get(
                assessment__id=assessment_id,
                assessment__client__id=self.request.user.client.id,
            )
        except MaterialityChangeConfirmation.DoesNotExist:
            return None

    def get(self, request, assessment_id, *args, **kwargs):
        confirmation = self.get_object(assessment_id)
        if confirmation is None:
            return Response(
                {"error": "MaterialityChangeConfirmation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MaterialityChangeConfirmationSerializer(confirmation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, assessment_id, *args, **kwargs):
        confirmation = self.get_object(assessment_id)
        if confirmation is None:
            return Response(
                {"error": "MaterialityChangeConfirmation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MaterialityChangeConfirmationSerializer(
            confirmation, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
