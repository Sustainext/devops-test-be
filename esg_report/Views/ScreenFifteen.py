from esg_report.models.ScreenFifteen import ScreenFifteenModel
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenFifteenSerializer import ScreenFifteenSerializer
from sustainapp.models import Report
from collections import defaultdict
from datametric.models import RawResponse
from esg_report.utils import (
    get_data_points_as_per_report,
    collect_data_and_differentiate_by_location,
    collect_data_by_raw_response_and_index,
    get_raw_responses_as_per_report,
    calling_analyse_view_with_params,
)


class ScreenFifteenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slugs = {
            0: "gri-social-product_safety-416-1a-number",
            1: "gri-social-compliance-416-2a-total_number",
            2: "gri-social-compliance-416-2b-statement",
            3: "gri-social-product_labeling-417-1a-required",
            4: "gri-social-product_labeling-417-1b-number",
            5: "gri-social-non_compliance_labeling-417-2a-incidents",
            6: "gri-social-statement_labeling-417-2b-statement",
            7: "gri-social-non_compliance_marketing-417-3a-incidents",
            8: "gri-social-statement_marketing-417-3b-statement",
            9: "gri-social-customer_privacy-418-1b-identified_leaks",
            10: "gri-social-customer_privacy-418-1c-statement",
        }

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
            serializer = ScreenFifteenSerializer(screen_fifteen, data=request.data)
        except ObjectDoesNotExist:
            serializer = ScreenFifteenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_fifteen: ScreenFifteenModel = self.report.screen_fifteen
            serializer = ScreenFifteenSerializer(screen_fifteen)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update()
        self.set_data_points()
        self.set_raw_responses()
        response_data["416_1a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0]),
        )
        response_data["416_1a_analyse"] = calling_analyse_view_with_params(
            view_url="get_customer_health_safety_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["416_2a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[1]),
        )
        response_data["416_2b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[2]),
        )
        response_data["417_1a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[3]),
        )
        response_data["417_1b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[4]),
        )
        response_data["417_2a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[5]),
        )
        response_data["417_2b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[6]),
        )
        response_data["417_1a_analysis"] = calling_analyse_view_with_params(
            view_url="get_marketing_and_labeling_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["417_3a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[7]),
        )
        response_data["417_3b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[8]),
        )
        response_data["418_1a_analyse"] = calling_analyse_view_with_params(
            view_url="get_customer_privacy_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["418_1b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[9]),
        )
        response_data["418_1c"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[10]),
        )
        response_data["3-3cde"] = None

        return Response(response_data, status=status.HTTP_200_OK)
