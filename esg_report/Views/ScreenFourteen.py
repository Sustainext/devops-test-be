from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenFourteen import ScreenFourteen
from datametric.models import RawResponse, DataMetric, DataPoint

from esg_report.Serializer.ScreenFourteenSerializer import ScreenFourteenSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.services.screen_fourteen_service import ScreenFourteenService


class ScreenFourteenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def put(self, request, report_id: int) -> Response:
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data: dict[str, Any] = {}
        try:
            screen_fourteen: ScreenFourteen = self.report.screen_fourteen
            serializer = ScreenFourteenSerializer(
                screen_fourteen,
                data=request.data,
                partial=True,
                context={"request": request},
            )
        except ObjectDoesNotExist:
            serializer = ScreenFourteenSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def get(self, request, report_id: int) -> Response:
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = ScreenFourteenService(
            report_id=report_id, request=request
        ).get_api_response()

        return Response(response_data, status=status.HTTP_200_OK)
