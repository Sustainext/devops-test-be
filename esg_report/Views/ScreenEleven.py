from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenEleven import ScreenEleven
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
)
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
            7: "gri-economic-climate_related_risks-202-2a-physical_risk",
            8: "gri-economic-climate_related_risks-202-2a-transition_risk",
            9: "gri-economic-climate_related_risks-202-2a-other_risk",
            10: "gri-economic-approach_to_tax-207-1a",
            11: "gri-economic-country_by_country_reporting-207-4a-please",
            12: "gri-economic-country_by_country_reporting-207-4b-for",
            13: "gri-economic-country_by_country_reporting-207-4c-disclosure",
            14: "gri-economic-tax_governance_control_and_risk_management-207-2a-provide",
            15: "gri-economic-tax_governance_control_and_risk_management-207-2b-description",
            16: "gri-economic-tax_governance_control_and_risk_management-207-2c-has",
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
        return Response(response_data, status=status.HTTP_200_OK)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_201_a_b(self):
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[0])
            .order_by("-year")
            .first()
        )
        local_response_data = {}
        local_data = local_raw_responses.data[0] if local_raw_responses else None
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
        local_data = local_raw_responses.data[0] if local_raw_responses else None
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

    def get_203_2a(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[5]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None

    def get_203_2b(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[6]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None

    def get_201_2a1(self):
        # * Note: There's no data point for this question, hence using raw response
        local_raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[7])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data if local_raw_response else None
        if not local_data:
            return local_data
        else:
            return local_data

    def get_201_2a2(self):
        # * Note: There's no data point for this question, hence using raw response
        local_raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[8])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data if local_raw_response else None
        if not local_data:
            return local_data
        else:
            return local_data

    def get_201_2a3(self):
        # * Note: There's no data point for this question, hence using raw response
        local_raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[9])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data if local_raw_response else None
        if not local_data:
            return local_data
        else:
            return local_data

    def get_201_2a_responses(self):

        return {
            "201_2a1": self.get_201_2a1(),
            "201_2a2": self.get_201_2a2(),
            "201_2a3": self.get_201_2a3(),
        }

    def get_207_1a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[10]).order_by(
            "-year"
        )
        response_data = {}
        name_mapping = {
            "Q1": "does_your_organisation_have_a_tax_strategy",
            "Q2": "provide_a_link_to_the_tax_strategy_if_it_is_publicly_available",
            "Q3": "mention_the_governance_body_or_executive-level_position_within_the_organization_that_formally_reviews_and_approves_the_tax_strategy",
            "Q4": "mention_the_frequency_the_tax_strategy_review",
            "Q5": "tax_compliance_approach",
            "Q6": "tax_approach_link_to_business_and_sustainability",
        }
        local_datametrics = DataMetric.objects.filter(path__slug=self.slugs[10])
        for data_metric in local_datametrics:
            try:
                response_data[name_mapping[data_metric.name]] = local_data_points.get(
                    data_metric=data_metric
                )
            except DataPoint.DoesNotExist:
                response_data[name_mapping[data_metric.name]] = None
        return response_data

    def get_207_4a(self):
        """
        #* Note: There's no data point for this question, hence using raw response
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[11])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_responses.data[0]["Q1"] if local_raw_responses else None
        return local_data

    def get_207_4b(self):
        """
        Note: Currency cannot be fetched from the data point, hence using raw response to get proper data.
        """
        local_raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[12])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data[0] if local_raw_response else None
        name_mapping = {
            "Taxjurisdictioncol1": "tax_jurisdiction",
            "Taxjurisdictioncol2": "names_of_resident_entities",
            "Taxjurisdictioncol3": "primary_activities_of_the_organization",
            "Taxjurisdictioncol4": "number_of_employees_and_calculation_basis",
            "Taxjurisdictioncol5": "revenues_from_third_party_sales",
            "Taxjurisdictioncol6": "intra_group_revenues_by_tax_jurisdiction",
            "Taxjurisdictioncol7": "profit_or_loss_before_tax",
            "Taxjurisdictioncol8": "tangible_assets_excluding_cash_equivalents",
            "Taxjurisdictioncol9": "corporate_income_tax_paid_on_a_cash_basis",
            "Taxjurisdictioncol10": "corporate_income_tax_accrued_on_profit_or_loss",
            "Taxjurisdictioncol11": "reasons_for_difference_in_accrued_and_statutory_tax",
        }
        response_data = {
            "currency": local_data.get("Q1"),
        }
        for table_dictionary in local_data.get("Q2"):
            for key, value in table_dictionary.items():
                response_data[name_mapping[key]] = value
        return response_data

    def get_207_4c(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[13]).order_by("-year").first()
        )
        return local_data_points.value if local_data_points else None

    def get_207_2a(self):
        local_data_points = (
            self.data_points.filter(path__slug=self.slugs[14]).order_by("-year").first()
        )
        name_mapping = {}

    def get_3_3cde(self):
        return None

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
        response_data["201_a_b"] = self.get_201_a_b()
        response_data["201_4ab"] = self.get_201_4ab()
        response_data["203_1a"] = self.get_203_1a()
        response_data["203_1b"] = self.get_203_1b()
        response_data["203_1c"] = self.get_203_1c()
        response_data["203_2a"] = self.get_203_2a()
        response_data["203_2b"] = self.get_203_2b()
        response_data["201_2a"] = self.get_201_2a_responses()
        response_data["207_1a"] = self.get_207_1a()
        response_data["207_4a"] = self.get_207_4a()
        response_data["207_4b"] = self.get_207_4b()
        response_data["207_4c"] = self.get_207_4c()
        response_data["207_2a"] = self.get_207_2a()
        response_data["3_3cde"] = self.get_3_3cde()

        return Response(response_data, status=status.HTTP_200_OK)
