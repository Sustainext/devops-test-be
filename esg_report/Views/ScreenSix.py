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
            response_data["engagement_with_stakeholders"] = (
                raw_responses.filter(path__slug=slugs[0]).first().data
                if raw_responses.filter(path__slug=slugs[0]).exists()
                else None
            )
            response_data["approach_to_stakeholder_engagement"] = [
                i[0]
                for i in raw_responses.filter(path__slug=slugs[1]).values_list(
                    "data", flat=True
                )
            ]
            # TODO: Modify the Stakeholder Feedback after materiality assessment selection logic is done
            materiality_assessment = MaterialityAssessment.objects.filter(
                start_date__gte=report.start_date,
                end_date__lte=report.end_date,
                client=report.client,
            ).first()
            try:
                response_data["stakeholder_feedback"] = (
                    materiality_assessment.management_approach_questions.stakeholder_engagement_effectiveness_description
                )
            except ObjectDoesNotExist:
                response_data["stakeholder_feedback"] = None
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Stakeholder engagement not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, report_id, format=None):
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
            stakeholder_engagement.delete()
        except ObjectDoesNotExist:
            # * Condition when API has to be behave like POST
            pass
        serializer = StakeholderEngagementSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data, status=status.HTTP_200_OK)
