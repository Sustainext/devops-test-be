from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenTen import ScreenTen
from materiality_dashboard.models import ManagementApproachQuestion
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import get_materiality_assessment
from esg_report.Serializer.ScreenTenSerializer import ScreenTenSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ScreenTenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slugs = {
            1: "gri-economic-proportion_of_spending_on_local_suppliers-percentage-204-1a",
            2: "gri-economic-proportion_of_spending_on_local_suppliers-organization-204-1b",
            3: "gri-economic-proportion_of_spending_on_local_suppliers-definition-204-1c",
        }

    def put(self, request, report_id: int) -> Response:
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data: dict[str, Any] = {}
        try:
            screen_ten: ScreenTen = report.screen_ten
            screen_ten.delete()
        except ObjectDoesNotExist:
            # * If the ScreenTen does not exist, create a new one
            pass
        serializer = ScreenTenSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        response_data.update(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_204_1abc_using_datapoint(self) -> dict[str, Any]:
        # * Get datapoint
        datapoint = DataPoint.objects.filter(path__slug=self.slugs[0]).filter(
            client_id=self.report.client.id
        ).filter(year__range=(self.report.start_date.year, self.report.end_date.year))
        

    def get_204_1abc(self) -> dict[str, Any]:
        response_data = {}
        # * 204-1a
        raw_responses = (
            RawResponse.objects.filter(path__slug=self.slugs[1])
            .filter(
                year__range=(self.report.start_date.year, self.report.end_date.year)
            )
            .filter(client=self.request.user.client)
        ).order_by("-year")
        if raw_responses.exists():
            response_data["204-1a"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1a"] = None

        # * 204-1b
        raw_responses = (
            RawResponse.objects.filter(path__slug=self.slugs[2])
            .filter(
                year__range=(self.report.start_date.year, self.report.end_date.year)
            )
            .filter(client=self.request.user.client)
        ).order_by("-year")
        if raw_responses.exists():
            response_data["204-1b"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1b"] = None

        # * 204-1c
        raw_responses = (
            RawResponse.objects.filter(path__slug=self.slugs[2])
            .filter(
                year__range=(self.report.start_date.year, self.report.end_date.year)
            )
            .filter(client=self.request.user.client)
        ).order_by("-year")
        if raw_responses.exists():
            response_data["204-1b"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1b"] = None

        return response_data

    def get(self, request, report_id: int) -> Response:
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data: dict[str, Any] = {}
        try:
            screen_ten: ScreenTen = self.report.screen_ten
            serializer = ScreenTenSerializer(screen_ten, context={"request": request})
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data["company_sustainability_statement"] = None
            response_data["approach_for_sustainability"] = None
            response_data["sustainability_goals"] = None
            response_data["approach_to_supply_chain_sustainability"] = None

        materiality_assessment = get_materiality_assessment(self.report)
        management_approach_question: ManagementApproachQuestion | None = (
            ManagementApproachQuestion.objects.filter(
                assessment=materiality_assessment
            ).first()
        )
        response_data["3-3cde"] = {}
        if not management_approach_question:
            response_data["3-3cde"][
                "negative_impact_involvement_description"
            ] = management_approach_question.negative_impact_involvement_description
            response_data["3-3cde"][
                "stakeholder_engagement_effectiveness_description"
            ] = (
                management_approach_question.stakeholder_engagement_effectiveness_description
            )
        else:
            response_data["3-3cde"]["negative_impact_involvement_description"] = None
            response_data["3-3cde"][
                "stakeholder_engagement_effectiveness_description"
            ] = None

        response_data.update(self.get_204_1abc(self.report))
        response_data["308-2-a"] = None
        response_data["308-2-b"] = None
        response_data["308-2-c"] = None
        response_data["414-2-a"] = None
        response_data["414-2-b"] = None
        response_data["414-2-c"] = None
        return Response(response_data, status=status.HTTP_200_OK)
