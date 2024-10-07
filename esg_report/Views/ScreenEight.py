from esg_report.models.ScreenEight import MaterialityStatement
from esg_report.Serializer.MaterialityStatementSerializer import (
    MaterialityStatementSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import get_latest_raw_response, get_materiality_dashboard
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityImpactSerializer import (
    MaterialityImpactSerializer,
)
from django.core.exceptions import ObjectDoesNotExist


class ScreenEightAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            materiality_statement: MaterialityStatement = report.materiality_statement
            materiality_statement.delete()
        except ObjectDoesNotExist:
            # * If the MaterialityStatement does not exist, create a new one
            pass
        serializer = MaterialityStatementSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            materiality_statement: MaterialityStatement = report.materiality_statement
            serializer = MaterialityStatementSerializer(
                materiality_statement, context={"request": request}
            )
            response_data = serializer.data
        except ObjectDoesNotExist:
            return Response(
                None,
                status=status.HTTP_200_OK,
            )
        materiality_assessment: MaterialityAssessment = get_materiality_dashboard(
            report
        )
        # TODO: Add list of materiality topics
        response_data["materiality_topics"] = {}
        try:
            response_data["3-2b"] = (
                materiality_assessment.change_confirmation.reason_for_change
            )
        except ObjectDoesNotExist:
            response_data["3-2b"] = None

        try:
            # TODO: Change this when management_approach_questions is changed to one to one relationship
            response_data["3-1-a"] = {
                "process_description": materiality_assessment.assessment_process.all()
                .get()
                .process_description,
                "impact_assessment_process": materiality_assessment.assessment_process.all()
                .get()
                .impact_assessment_process,
                "selected_stakeholders": list(
                    materiality_assessment.assessment_process.all()
                    .get()
                    .selected_stakeholders.all()
                    .values_list("name", flat=True)
                ),
            }

        except ObjectDoesNotExist:
            response_data["3-1-a"] = None

        try:
            response_data["3-3a"] = MaterialityImpactSerializer(
                materiality_assessment.management_impacts.all(), many=True
            ).data
        except ObjectDoesNotExist:
            response_data["3-3a"] = None

        try:
            # TODO: Change this when management_approach_questions is changed to one to one relationship
            response_data["3-3b"] = (
                materiality_assessment.management_approach_questions.all()
                .get()
                .negative_impact_involvement_description
            )
        except ObjectDoesNotExist:
            response_data["3-3b"] = None

        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            materiality_statement: MaterialityStatement = report.materiality_statement
            materiality_statement.delete()
        except ObjectDoesNotExist:
            # * If the MaterialityStatement does not exist, create a new one
            pass
        serializer = MaterialityStatementSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
