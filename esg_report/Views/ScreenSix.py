from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.models.ScreenSix import StakeholderEngagement
from materiality_dashboard.models import MaterialityAssessment
from esg_report.Serializer.StakeholderEngagementSerializer import (
    StakeholderEngagementSerializer,
)
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import get_materiality_assessment


class ScreenSixAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            stakeholder_engagement: StakeholderEngagement = (
                report.stakeholder_engagement
            )
            serializer = StakeholderEngagementSerializer(stakeholder_engagement)
            slugs = [
                "gri-general-stakeholder_engagement-2-29a-describe",
                "gri-general-stakeholder_engagement-2-29b-stakeholder",
            ]
            raw_responses = (
                RawResponse.objects.filter(path__slug__in=slugs)
                .filter(year__range=(report.start_date.year, report.end_date.year))
                .filter(client=self.request.user.client)
            ).order_by("-year")
            response_data = serializer.data
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
            response_data["approach_to_stakeholder_engagement"] = [
                i[0]
                for i in raw_responses.filter(path__slug=slugs[1]).values_list(
                    "data", flat=True
                )
            ]
            # TODO: Change the getting stakeholder_feedback from materiality assessment ones relationship converts to OneToOne Field
            materiality_assessment = get_materiality_assessment(report)
            try:
                response_data["stakeholder_feedback"] = (
                    materiality_assessment.management_approach_questions.all()
                    .first()
                    .stakeholder_engagement_effectiveness_description
                )
            except (ObjectDoesNotExist, AttributeError):
                response_data["stakeholder_feedback"] = None
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                None,
                status=status.HTTP_200_OK,
            )

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            stakeholder_engagement: StakeholderEngagement = (
                report.stakeholder_engagement
            )
            serializer = StakeholderEngagementSerializer(
                stakeholder_engagement, data=request.data
            )
        except ObjectDoesNotExist:
            serializer = StakeholderEngagementSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)
