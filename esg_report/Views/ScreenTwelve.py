from esg_report.models.ScreenTwelve import ScreenTwelve
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenTwelveSerializer import ScreenTwelveSerializer
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
)


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
            serializer = ScreenTwelveSerializer(screen_twelve, data=request.data)
        except ObjectDoesNotExist:
            serializer = ScreenTwelveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.slugs = {}

    def get_3_3cde(self):
        #TODO: Materiality Assessment Screen is pending
        return None
    
    

    def get(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_twelve: ScreenTwelve = self.report.screen_twelve
            serializer = ScreenTwelveSerializer(screen_twelve)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenTwelve._meta.fields
                    if field.name not in ["id", "report"]
                }
            )

        self.set_raw_responses()
        self.set_data_points()

        return Response(response_data, status=status.HTTP_200_OK)
