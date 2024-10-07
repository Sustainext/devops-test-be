from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.models.ScreenSix import StakeholderEngagement
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
            )
            response_data = serializer.data
            response_data["engagement_with_stakeholders"] = [
                i[0]
                for i in raw_responses.filter(path__slug=slugs[0]).values_list(
                    "data", flat=True
                )
            ]
            response_data["approach_to_stakeholder_engagement"] = [
                i[0]
                for i in raw_responses.filter(path__slug=slugs[1]).values_list(
                    "data", flat=True
                )
            ]
            # TODO: Add Stakeholder Feedback
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
