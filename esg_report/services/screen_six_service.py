from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from esg_report.Serializer.StakeholderEngagementSerializer import (
    StakeholderEngagementSerializer,
)
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import get_materiality_assessment


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

            # Define slugs and fetch raw responses
            slugs = [
                "gri-general-stakeholder_engagement-2-29a-describe",
                "gri-general-stakeholder_engagement-2-29b-stakeholder",
            ]
            raw_responses = (
                RawResponse.objects.filter(path__slug__in=slugs)
                .filter(year__range=(report.start_date.year, report.end_date.year))
                .filter(client=user.client)
            ).order_by("-year")

            # Process the first slug's response
            if raw_responses.filter(path__slug=slugs[0]).exists():
                response_data.update(
                    raw_responses.filter(path__slug=slugs[0]).first().data[0]
                )
            else:
                response_data.update(
                    {
                        "Organisationengages": None,
                        "Stakeholdersidentified": None,
                        "Stakeholderengagement": None,
                    }
                )

            # Process the second slug's response for engagement approach
            response_data["approach_to_stakeholder_engagement"] = [
                i[0]
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
        except ObjectDoesNotExist:
            return None
