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
from esg_report.utils import get_materiality_assessment, get_raw_responses_as_per_report


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
            response_data = serializer.data
        except ObjectDoesNotExist:
            # * Add model fields with None values as a dictionary
            response_data = {"description": None, "report": report_id}
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


        response_data["approach_to_stakeholder_engagement"] = [
            i
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
        report.last_updated_by = request.user
        report.save()
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)
