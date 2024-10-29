from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenNine import ScreenNine
from datametric.models import RawResponse
from esg_report.Serializer.ScreenNineSerializer import ScreenNineSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from esg_report.services.screen_nine_service import ScreenNineService


class ScreenNineView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def put(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ScreenNineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer = ScreenNineSerializer(
                instance=self.report.screen_nine, data=request.data
            )
        except ObjectDoesNotExist:
            serializer = ScreenNineSerializer(data=request.data)
        serializer.save(report=self.report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, report_id):
        # TODO: Apply this optimisation in self.raw_responses. (https://chatgpt.com/share/66fd7656-1684-8008-b95e-b3b26ccb1aae)
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        screen_nine_data = ScreenNineService(report_id=report_id)
        response_data = screen_nine_data.get_response()

        return Response(response_data, status=status.HTTP_200_OK)
