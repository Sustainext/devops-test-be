from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from esg_report.Serializer.StakeholderEngagementSerializer import (
    StakeholderEngagementSerializer,
)
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import get_materiality_assessment, get_raw_responses_as_per_report


class StakeholderEngagementService:
    @staticmethod
    def get_stakeholder_engagement_by_report_id(report_id, user):
        """
        Fetches and prepares stakeholder engagement data for a specific report.
        """
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return {"error": "Report not found", "status": status.HTTP_404_NOT_FOUND}

        try:
            stakeholder_engagement = report.stakeholder_engagement
            serializer = StakeholderEngagementSerializer(stakeholder_engagement)
            response_data = serializer.data
        except ObjectDoesNotExist:
            response_data = {"description": None, "report": report_id}
        # Define slugs and fetch raw responses
        slugs = [
            "gri-general-stakeholder_engagement-2-29a-describe",
            "gri-general-stakeholder_engagement-2-29b-stakeholder",
        ]
        raw_responses = get_raw_responses_as_per_report(report)

        
        if raw_responses.filter(path__slug=slugs[0]).exists():
            try:
                data_entries = raw_responses.filter(path__slug=slugs[0]).first().data
              
                response_data["Organisationengages"] = [
                    entry.get("Organisationengages", "") for entry in data_entries
                ]
                response_data["Stakeholdersidentified"] = [
                    entry.get("Stakeholdersidentified", "") for entry in data_entries
                ]
                response_data["Stakeholderengagement"] = [
                    entry.get("Stakeholderengagement", "") for entry in data_entries
                ]
            except Exception:
                response_data["Organisationengages"] = []
                response_data["Stakeholdersidentified"] = []
                response_data["Stakeholderengagement"] = []
        else:
            response_data["Organisationengages"] = []
            response_data["Stakeholdersidentified"] = []
            response_data["Stakeholderengagement"] = []


        # Process the second slug's response for engagement approach
        response_data["approach_to_stakeholder_engagement"] = [
            i
            for i in raw_responses.filter(path__slug=slugs[1]).values_list(
                "data", flat=True
            )
        ]

        # Get materiality assessment data
        materiality_assessment = get_materiality_assessment(report)
        try:
            response_data["stakeholder_feedback"] = (
                materiality_assessment.management_approach_questions.all()
                .first()
                .stakeholder_engagement_effectiveness_description
            )
        except (ObjectDoesNotExist, AttributeError):
            response_data["stakeholder_feedback"] = None

        return response_data
