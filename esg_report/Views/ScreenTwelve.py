from esg_report.models.ScreenTwelve import ScreenTwelve
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Report
from esg_report.Serializer.ScreenTwelveSerializer import ScreenTwelveSerializer
from django.core.exceptions import ObjectDoesNotExist
from esg_report.services.screen_twelve_service import ScreenTwelveService


class ScreenTwelveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_twelve: ScreenTwelve = self.report.screen_twelve
            serializer = ScreenTwelveSerializer(
                screen_twelve,
                data=request.data,
                partial=True,
                context={"request": request},
            )
        except ObjectDoesNotExist:
            serializer = ScreenTwelveSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        screen_twelve_service = ScreenTwelveService(self.report.id, request)
        response_data = screen_twelve_service.get_api_response()
        return Response(response_data, status=status.HTTP_200_OK)
