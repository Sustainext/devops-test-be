from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenEleven import ScreenEleven
from esg_report.Serializer.ScreenElevenSerializer import ScreenElevenSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from esg_report.services.screen_eleven_service import ScreenElevenService
from django.core.exceptions import ObjectDoesNotExist


class ScreenElevenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def put(self, request, report_id: int) -> Response:
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data: dict[str, Any] = {}
        try:
            screen_eleven: ScreenEleven = report.screen_eleven
            screen_eleven.delete()
        except ObjectDoesNotExist:
            # * If the ScreenEleven does not exist, create a new one
            pass
        serializer = ScreenElevenSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def get(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        screen_eleven_service = ScreenElevenService(
            report_id=report_id, request=request
        )
        response_data = screen_eleven_service.get_api_response()

        return Response(response_data, status=status.HTTP_200_OK)
