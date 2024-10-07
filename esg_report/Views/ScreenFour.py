from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.Serializer.SustainabilityRoadmapSerializer import (
    SustainabilityRoadmapSerializer,
)
from esg_report.models.ScreenFour import SustainabilityRoadmap
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ScreenFourAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            sustainability_roadmap = report.sustainability_roadmap
        except (SustainabilityRoadmap.DoesNotExist, ObjectDoesNotExist):
            return Response(
                None,
                status=status.HTTP_200_OK,
            )
        serializer = SustainabilityRoadmapSerializer(sustainability_roadmap)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            sustainability_roadmap = report.sustainability_roadmap
            sustainability_roadmap.delete()
        except (SustainabilityRoadmap.DoesNotExist, ObjectDoesNotExist):
            # * If the sustainability roadmap does not exist, create a new one
            pass
        serializer = SustainabilityRoadmapSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data, status=status.HTTP_200_OK)
