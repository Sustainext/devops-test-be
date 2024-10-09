from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenEleven import ScreenEleven
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import get_materiality_assessment
from esg_report.Serializer.ScreenElevenSerializer import ScreenElevenSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class ScreenElevenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.slugs = {
            0: "gri-economic-direct_economic_value-report-201-1a-1b",
            1: "gri-economic-financial_assistance-204-1a-2b-provide",
            2: "gri-economic-infrastructure-describe-203-1a",
            3: "gri-economic-infrastructure-explain-203-1b",
            4: "gri-economic-infrastructure-whether-203-1c",
            5: "gri-economic-significant_indirect-provide-203-2a",
            6: "gri-economic-significant_indirect-explain-203-2b",
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
            screen_eleven: ScreenEleven = report.screen_eleven
            screen_eleven.delete()
        except ObjectDoesNotExist:
            # * If the ScreenEleven does not exist, create a new one
            pass
        serializer = ScreenElevenSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(client_id=self.request.user.client.id)
            .filter(Q(organization=self.report.organization))
            .filter(path__slug=self.slugs[1])
        )
        if self.report.corporate.location.all().exists():
            self.data_points = self.data_points.filter(
                Q(corporate=self.report.corporate)
                | Q(locale__in=self.report.corporate.location.all())
            )

    def set_raw_responses(self):
        self.raw_responses = (
            RawResponse.objects.filter(client=self.report.client)
            .filter(
                Q(organization=self.report.organization)
                | Q(corporate=self.report.corporate)
            )
            .filter(path__slug=self.slugs[1])
        )

    def get_201ab(self):
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[0])
            .order_by("-year")
            .first()
        )
        local_response_data = {}
        local_data = local_raw_responses.data if local_raw_responses else None
        if not local_data:
            return local_data
        local_response_data["201-1a"] = {}
        local_response_data["201-1a"]["currency"] = local_data.get("Q1")
        local_response_data["201-1a"]["revenues"] = local_data.get("Q2")
        local_response_data["201-1a"]["economic_value_distributed"] = local_data.get(
            "Q3"
        )
        local_response_data["201-1a"]["operating_costs"] = local_data.get("Q4")
        local_response_data["201-1a"]["employee_wages_benefits"] = local_data.get("Q5")
        local_response_data["201-1a"]["payments_to_providers_of_capital"] = (
            local_data.get("Q6")
        )
        local_response_data["201-1a"]["payments_to_governments_by_country"] = (
            local_data.get("Q7")
        )
        local_response_data["201-1a"]["countries_and_payments"] = local_data.get("Q8")
        local_response_data["201-1a"]["community_investments"] = local_data.get("Q9")
        local_response_data["201-1a"]["direct_economic_value_generated"] = (
            local_data.get("Q10")
        )
        local_response_data["201-1a"]["economic_value_distributed"] = local_data.get(
            "Q11"
        )
        return local_data

    def get_201_4ab(self):
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[1])
            .order_by("-year")
            .first()
        )
        local_response_data = {}
        local_data = local_raw_responses.data if local_raw_responses else None
        if not local_data:
            return local_data
        local_response_data["currency"] = local_data.get("Q1")
        local_response_data["tax_relief_and_tax_credits"] = local_data.get("Q2")
        local_response_data["subsidies"] = local_data.get("Q3")
        local_response_data[
            "provide_details_of_investment_grants_research_and_development_grants_and_other_relevant_types_of_grant"
        ] = local_data.get("Q4")
        local_response_data["awards"] = local_data.get("Q5")
        local_response_data["royalty_holidays"] = local_data.get("Q6")
        local_response_data["financial_assistance_from_export_credit_agencies"] = (
            local_data.get("Q7")
        )
        local_response_data["financial_incentives"] = local_data.get("Q8")
        local_response_data[
            "other_financial_benefits_received_or_receivable_from_any_government_for_any_operation"
        ] = local_data.get("Q9")
        return local_response_data

    def get_203_1a(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[2]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None

    def get_203_1b(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[3]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None

    def get_203_1c(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[4]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None



    def get(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        self.set_data_points()
        self.set_raw_responses()
        try:
            screen_eleven = self.report.screen_eleven
            serializer = ScreenElevenSerializer(screen_eleven)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    "company_economic_performance_statement": None,
                    "financial_assistance_from_government": None,
                }
            )
        response_data["201_ab"] = self.get_201ab()
        response_data["201_4ab"] = self.get_201_4ab()
        response_data["203_1a"] = self.get_203_1a()
        response_data["203_1b"] = self.get_203_1b()
        response_data["203_1c"] = self.get_203_1c()

        return Response(response_data, status=status.HTTP_200_OK)
