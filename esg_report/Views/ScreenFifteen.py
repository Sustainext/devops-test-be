from esg_report.models.ScreenFifteen import ScreenFifteenModel
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenFifteenSerializer import ScreenFifteenSerializer
from sustainapp.models import Report
from esg_report.services.screen_fifteen_service import ScreenFifteenService


class ScreenFifteenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def put(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_fifteen: ScreenFifteenModel = self.report.screen_fifteen
            serializer = ScreenFifteenSerializer(
                screen_fifteen,
                data=request.data,
                partial=True,
                context={"request": request},
            )
        except ObjectDoesNotExist:
            serializer = ScreenFifteenSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def get(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = ScreenFifteenService(
            request=request, report_id=report_id
        ).get_api_response()

        return Response(response_data, status=status.HTTP_200_OK)
