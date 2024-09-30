from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenThree import MissionVisionValues
from sustainapp.models import Report
from esg_report.Serializer.MissionVisionValuesSerializer import (
    MissionVisionValuesSerializer,
)
from rest_framework.permissions import IsAuthenticated


class ScreenThreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            mission_vision_values = report.mission_vision_values
        except MissionVisionValues.DoesNotExist:
            return Response(
                {"error": "Mission Vision Values not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MissionVisionValuesSerializer(mission_vision_values)
        return Response(serializer.data)

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            mission_vision_values = report.mission_vision_values
        except MissionVisionValues.DoesNotExist:
            return Response(
                {"error": "Mission Vision Values not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MissionVisionValuesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mission_vision_values.delete()
        serializer.save(report=report)
        return Response(serializer.data)
