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
from django.db.models import Q


class ScreenTenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slugs = {
            1: "gri-economic-proportion_of_spending_on_local_suppliers-percentage-204-1a",
            2: "gri-economic-proportion_of_spending_on_local_suppliers-organization-204-1b",
            3: "gri-economic-proportion_of_spending_on_local_suppliers-definition-204-1c",
            4: "gri-social-supplier_screened-414-1a-number_of_new_suppliers",
            5: "gri-social-impacts_and_actions-414-2a-2d-2e-negative_social_impacts",
            6: "gri-social-impacts_and_actions-414-2b-number_of_suppliers",
            7: "gri-social-impacts_and_actions-414-2c-significant_actual",
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

    def set_raw_responses(self):
        self.raw_responses = RawResponse.objects.filter(
            year__range=(self.report.start_date.year, self.report.end_date.year)
        ).filter(client=self.request.user.client)

        if self.report.organization or self.report.corporate:
            self.raw_responses = self.raw_responses.filter(
                Q(organization=self.report.organization)
                | Q(corporate=self.report.corporate)
            )
        if self.report.corporate:
            self.raw_responses = self.raw_responses.filter(
                Q(locale__in=self.report.corporate.location.all())
            )

    def get_204_1abc_using_datapoint(self) -> dict[str, Any]:
        # * Get datapoint
        datapoint = (
            (
                DataPoint.objects.filter(path__slug=self.slugs[0])
                .filter(client_id=self.report.client.id)
                .filter(
                    year__range=(self.report.start_date.year, self.report.end_date.year)
                )
            )
            .order_by("-year")
            .first()
        )
        # TODO: Complete the method.

    def get_204_1abc(self) -> dict[str, Any]:
        response_data = {}
        # * 204-1a
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[1])).order_by(
            "-year"
        )
        if raw_responses.exists():
            response_data["204-1a"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1a"] = None

        # * 204-1b
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[2])).order_by(
            "-year"
        )
        if raw_responses.exists():
            response_data["204-1b"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1b"] = None

        # * 204-1c
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[2])).order_by(
            "-year"
        )
        if raw_responses.exists():
            response_data["204-1b"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1b"] = None

        return response_data

    def get_404_1abc(self) -> dict[str, Any]:
        response_data = {}
        # * 414-1a
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[4])).order_by(
            "-year"
        )
        response_data["414-1a"] = {}
        if raw_responses.exists():
            response_data["414-1a"][
                "number_of_new_suppliers_that_were_screened_using_social_criteria"
            ] = raw_responses.first().data[0]["Q1"]
            response_data["414-1a"][
                "total_number_of_suppliers"
            ] = raw_responses.first().data[0]["Q2"]
        else:
            response_data["414-1a"][
                "number_of_new_suppliers_that_were_screened_using_social_criteria"
            ] = None
            response_data["414-1a"]["total_number_of_suppliers"] = None
        return response_data

    def get_404_2abc(self) -> dict[str, Any]:
        response_data = {}
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[5])).order_by(
            "-year"
        )
        local_data = raw_responses.first().data[0]
        response_data["414-2a"] = {}
        if raw_responses.exists():
            response_data["414-2a"]["total_suppliers_terminated_negative_impact"] = (
                local_data["Q1"]
            )
            response_data["414-2a"]["total_suppliers_improved_negative_impact"] = (
                local_data["Q2"]
            )
            response_data["414-2a"]["total_suppliers_assessed_social_impact"] = (
                local_data["Q3"]
            )
        else:
            response_data["414-2a"]["total_suppliers_terminated_negative_impact"] = None
            response_data["414-2a"]["total_suppliers_improved_negative_impact"] = None
            response_data["414-2a"]["total_suppliers_assessed_social_impact"] = None

        response_data["414-2b"] = {}
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[6])).order_by(
            "-year"
        )
        if raw_responses.exists():
            response_data["414-2b"] = raw_responses.first().data
        else:
            response_data["414-2b"] = None

        raw_responses = self.raw_responses.filter(path__slug=self.slugs[7]).order_by(
            "-year"
        )
        response_data["414-2c"] = {}
        if raw_responses.exists():
            response_data["414-2c"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["414-2c"] = None
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
        self.set_raw_responses()
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

        response_data.update(self.get_204_1abc())
        response_data["308-2-a"] = None
        response_data["308-2-b"] = None
        response_data["308-2-c"] = None
        response_data.update(self.get_404_2abc())

        return Response(response_data, status=status.HTTP_200_OK)
