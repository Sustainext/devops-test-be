from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenSeven import AboutTheReport
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.Serializer.AboutTheReportSerializer import (
    AboutTheReportSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.utils import get_raw_responses_as_per_report

class ScreenSevenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            about_the_report: AboutTheReport = report.about_the_report
            serializer = AboutTheReportSerializer(about_the_report)
            response_data = serializer.data
        except ObjectDoesNotExist:
            response_data = {
                "report": report.id,
                "description": None,
                "framework_description": None,
                "external_assurance": None,
            }
        slugs = [
            "gri-general-report_details-reporting_period-2-3-a",
            "gri-general-report_details-point-2-3-d",
            "gri-general-restatements-2-4-a",
            "gri-general-assurance-policy-2-5-a",
            "gri-general-assurance-highest-2-5-a",
            "gri-general-assurance-external-2-5-b",
        ]
        raw_responses = get_raw_responses_as_per_report(report)
        response_data["2-3-a"] = (
            raw_responses.filter(path__slug=slugs[0]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[0]).order_by("year").first() is not None
            else None
        )
        response_data["2-3d"] = (
            raw_responses.filter(path__slug=slugs[1]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[1]).order_by("year").first() is not None
            else None
        )
        response_data["2-4-a"] = (
            raw_responses.filter(path__slug=slugs[2]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[2]).order_by("year").first() is not None
            else None
        )
        response_data["2-5-a"] = {}
        response_data["2-5-a"]["assurance-policy"] = (
            raw_responses.filter(path__slug=slugs[3]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[3]).order_by("year").first() is not None
            else None
        )
        response_data["2-5-a"]["assurance-highest"] = (
            raw_responses.filter(path__slug=slugs[4]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[4]).order_by("year").first() is not None
            else None
        )
        response_data["2-5-b"] = (
            raw_responses.filter(path__slug=slugs[5]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[5]).order_by("year").first() is not None
            else None
        )

        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            about_the_report: AboutTheReport = report.about_the_report
            about_the_report.delete()
        except ObjectDoesNotExist:
            # * If the About The Report does not exist, create a new one
            pass

        serializer = AboutTheReportSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data)
