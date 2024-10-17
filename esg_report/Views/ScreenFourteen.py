from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenFourteen import ScreenFourteen
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_maximum_months_year,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    forward_request_with_jwt,
)
from esg_report.Serializer.ScreenFourteenSerializer import ScreenFourteenSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from sustainapp.Utilities.community_engagement_analysis import (
    get_community_engagement_analysis,
)


class ScreenFourteenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.slugs = {0: "gri-social-impact_on_community-407-1a-operations"}

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
                screen_fourteen, data=request.data, context={"request": request}
            )
        except ObjectDoesNotExist:
            serializer = ScreenFourteenSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_413_1a(self):
        slug = "gri-social-community_engagement-413-1a-number_of_operations"
        raw_responses = self.raw_responses.filter(path__slug=slug)
        return get_community_engagement_analysis(
            raw_responses=raw_responses, slugs=slug
        )

    def get(self, request, report_id: int) -> Response:
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
                screen_fourteen, context={"request": request}
            )
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenFourteen._meta.fields
                    if field.name not in ["id", "report"]
                }
            )
        self.set_data_points()
        self.set_raw_responses()
        response_data["413_2a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[0])
        )
        response_data["413_1a_analyse"] = self.get_413_1a()
        response_data["3_3cde"] = (
            None  # TODO: Complete when materiality assessment screen is ready.
        )

        return Response(response_data, status=status.HTTP_200_OK)
