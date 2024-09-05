from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import MaterialityImpact
from materiality_dashboard.Serializers.MaterialityImpactSerializer import (
    MaterialityImpactSerializer,
    MaterialityImpactBulkSerializer,
)
from rest_framework.permissions import IsAuthenticated


class MaterialityImpactCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MaterialityImpactBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialityImpactEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, assessment_id, pk):
        try:
            return MaterialityImpact.objects.get(
                assessment__id=assessment_id,
                pk=pk,
                assessment__client__id=self.request.user.client.id,
            )
        except MaterialityImpact.DoesNotExist:
            return None

    def put(self, request, assessment_id, pk, *args, **kwargs):
        materiality_impact = self.get_object(assessment_id, pk)
        if materiality_impact is None:
            return Response(
                {"error": "MaterialityImpact not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MaterialityImpactSerializer(materiality_impact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialityImpactListAPIView(APIView):
    def get(self, request, assessment_id, *args, **kwargs):
        impacts = MaterialityImpact.objects.filter(
            assessment__id=assessment_id,
            assessment__client__id=self.request.user.client.id,
        )
        serializer = MaterialityImpactSerializer(impacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
