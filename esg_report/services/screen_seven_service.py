from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.AboutTheReportSerializer import (
    AboutTheReportSerializer,
)
from sustainapp.models import Report
from datametric.models import RawResponse
from common.utils.report_datapoint_utils import get_raw_responses_as_per_report


# TODO: We have to unify this service with report api response.
#! Possible errors can come.
class AboutTheReportService:
    @staticmethod
    def get_about_the_report_data(report_id, user):
        """
        Fetches and prepares about the report data for a specific report.
        """
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return {"error": "Report not found"}, None

        try:
            about_the_report = report.about_the_report
            serializer = AboutTheReportSerializer(about_the_report)
            response_data = serializer.data
        except ObjectDoesNotExist:
            response_data = {
                "report": report.id,
                "description": None,
                "framework_description": None,
                "external_assurance": None,
            }

        # Define slugs for required data
        slugs = [
            "gri-general-report_details-reporting_period-2-3-a",
            "gri-general-report_details-reporting_period-2-3-b",  
            "gri-general-report_details-publication-2-3-c",       
            "gri-general-report_details-point-2-3-d",
            "gri-general-restatements-2-4-a",
            "gri-general-assurance-policy-2-5-a",
            "gri-general-assurance-highest-2-5-a",
            "gri-general-assurance-external-2-5-b",
        ]

        # Retrieve raw responses based on slug and report date range
        raw_responses = get_raw_responses_as_per_report(report=report)

        # Map slug responses to response data with default handling
        response_data["2-3-a"] = (
            raw_responses.filter(path__slug=slugs[0]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[0]).order_by("year").first()
            else None
        )
        response_data["2-3-b"] = (
            raw_responses.filter(path__slug=slugs[1]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[1]).order_by("year").first()
            else None
        )
        response_data["2-3-c"] = (
            raw_responses.filter(path__slug=slugs[2]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[2]).order_by("year").first()
            else None
        )
        response_data["2-3-d"] = (
            raw_responses.filter(path__slug=slugs[3]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[3]).order_by("year").first()
            else None
        )
        response_data["2-4-a"] = (
            raw_responses.filter(path__slug=slugs[4]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[4]).order_by("year").first()
            else None
        )
        response_data["2-5-a"] = {
            "assurance_policy": (
                raw_responses.filter(path__slug=slugs[5]).order_by("year").first().data[0]
                if raw_responses.filter(path__slug=slugs[5]).order_by("year").first()
                else None
            ),
            "assurance_highest": (
                raw_responses.filter(path__slug=slugs[6]).order_by("year").first().data[0]
                if raw_responses.filter(path__slug=slugs[6]).order_by("year").first()
                else None
            ),
        }
        response_data["2-5-b"] = (
            raw_responses.filter(path__slug=slugs[7]).order_by("year").first().data[0]
            if raw_responses.filter(path__slug=slugs[7]).order_by("year").first()
            else None
        )

        return response_data
