from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenFive import AwardAndRecognition
from sustainapp.models import Report
from esg_report.Serializer.AwardsAndRecognitionSerializer import (
    AwardsAndRecognitionSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ScreenFiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            award_and_recognition: AwardAndRecognition = report.award_recognition
            serializer = AwardsAndRecognitionSerializer(award_and_recognition)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                None,
                status=status.HTTP_200_OK,
            )

    def put(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            award_and_recognition: AwardAndRecognition = report.award_recognition
            serializer = AwardsAndRecognitionSerializer(
                award_and_recognition, data=request.data
            )
        except ObjectDoesNotExist:
            serializer = AwardsAndRecognitionSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        report.last_updated_by = request.user
        report.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
