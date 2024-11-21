from sustainapp.models import Report
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_maximum_months_year,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    forward_request_with_jwt,
)
from sustainapp.Views.Analyse.Economic.CommunicationTraining import (
    CommunicationTrainingAnalyzeView,
)
from sustainapp.Views.Analyse.Economic.MarketPresenseAnalyse import (
    MarketPresenceAnalyseView,
)
from sustainapp.Views.Analyse.Economic.OperationsAssesedAnalyse import (
    OperationsAssessedAnalyzeView,
)
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenElevenSerializer import ScreenElevenSerializer


class ScreenElevenService:
    def __init__(self, report_id, request):
        self.report = Report.objects.get(id=report_id)
        self.request = request
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
            17: "gri-economic-stakeholder_engagement-207-3a",
            18: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3a-s1",
            19: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3b-s2",
            20: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3c-s3",
            21: "gri-economic-operations_assessed_for_risks_related_to_corruption-205-1a-total",
            22: "gri-economic-anti_corruption-comm_and_training-205-2a-governance_body_members",
            23: "gri-economic-anti_corruption-comm_and_training-205-2b-employees",
            24: "gri-economic-anti_corruption-comm_and_training-205-2c-business",
            25: "gri-economic-anti_corruption-comm_and_training-205-2d-training",
            26: "gri-economic-anti_corruption-comm_and_training-205-2e-policies",
            27: "gri-economic-financial_implications-201-2a-calculate",
            28: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3a-s1",
            29: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3b-s2",
            30: "gri-economic_confirmed_incidents_of_corruption_and_actions_taken-205-3c-s3",
            31: "gri-economic-public_legal_cases-205-3d",
            32: "gri-economic-climate_realted_opportunities-202-2a-report",
        }

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_communication_training_analyze(self):
        data = forward_request_with_jwt(
            view_class=CommunicationTrainingAnalyzeView,
            original_request=self.request,
            url="sustainapp/get_economic_communication_and_training/",
            query_params={
                "organisation": f"{self.report.organization.id}",
                "corporate": (
                    self.report.corporate.id
                    if self.report.corporate is not None
                    else ""
                ),  # Empty string as per your URL
                "location": "",  # Empty string
                "start": self.report.start_date.strftime("%Y-%m-%d"),
                "end": self.report.end_date.strftime("%Y-%m-%d"),
            },
        )
        return data

    def get_market_presence_analyze(self):
        data = forward_request_with_jwt(
            view_class=MarketPresenceAnalyseView,
            original_request=self.request,
            url="sustainapp/get_economic_market_presence/",
            query_params={
                "organisation": f"{self.report.organization.id}",
                "corporate": (
                    self.report.corporate.id
                    if self.report.corporate is not None
                    else ""
                ),  # Empty string as per your URL
                "location": "",  # Empty string
                "start": self.report.start_date.strftime("%Y-%m-%d"),
                "end": self.report.end_date.strftime("%Y-%m-%d"),
            },
        )
        return data

    def get_operations_assessed_analyze(self):
        data = forward_request_with_jwt(
            view_class=OperationsAssessedAnalyzeView,
            original_request=self.request,
            url="sustainapp/get_economic_operations_assessed/",
            query_params={
                "organisation": f"{self.report.organization.id}",
                "corporate": (
                    self.report.corporate.id
                    if self.report.corporate is not None
                    else ""
                ),  # Empty string as per your URL
                "location": "",  # Empty string
                "start": self.report.start_date.strftime("%Y-%m-%d"),
                "end": self.report.end_date.strftime("%Y-%m-%d"),
            },
        )
        return data

    def get_201_1ab(self):
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
        local_response_data["201-1a"]["economic_value_distributed_1"] = local_data.get(
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
        local_response_data["201-1a"]["economic_value_distributed_2"] = local_data.get(
            "Q11"
        )
        return local_response_data["201-1a"]

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
        local_data_points = self.data_points.filter(path__slug=self.slugs[2])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_203_1b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[3])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_203_1c(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[4])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_203_2a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[5])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_203_2b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[6])
        return collect_data_by_raw_response_and_index(local_data_points)

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
        return collect_data_by_raw_response_and_index(local_data_points)

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
        if not local_data:
            return local_data
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
        for index, table_dictionary in enumerate(local_data.get("Q2")):
            response_data[index] = {}
            for key, value in table_dictionary.items():
                response_data[index][name_mapping[key]] = value
        return response_data

    def get_207_4c(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[13])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_207_2a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[14]).order_by(
            "-year"
        )
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_207_2b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[15])
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_207_2c(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[16]).order_by(
            "-year"
        )
        response_data = {}
        local_data_metrics = DataMetric.objects.filter(path__slug=self.slugs[16])
        for data_metric in local_data_metrics:
            try:
                response_data[data_metric.name] = local_data_points.get(
                    data_metric=data_metric
                ).value
            except DataPoint.DoesNotExist:
                response_data[data_metric.name] = None
        return response_data

    def get_3_3cde(self):
        return None

    def get_207_3a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[17]).order_by(
            "-year"
        )
        response_data = {}
        local_data_metrics = DataMetric.objects.filter(path__slug=self.slugs[17])
        for data_metric in local_data_metrics:
            try:
                response_data[data_metric.name] = local_data_points.get(
                    data_metric=data_metric
                ).value
            except DataPoint.DoesNotExist:
                response_data[data_metric.name] = None
        return response_data

    def get_205_3a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[18]).order_by(
            "-year"
        )
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_205_3b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[19]).order_by(
            "-year"
        )
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_205_3c(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[20]).order_by(
            "-year"
        )
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_205_1a(self):
        return collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[21])
        )

    def get_205_2a(self):
        """
        Note: Data Metrics are messed up, hence using raw response to get proper data.
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[22])
            .order_by("-year")
            .first()
        )

        local_data = (
            local_raw_responses.data[0]["Q1"][0] if local_raw_responses else None
        )
        return local_data

    def get_205_2b(self):
        """
        Note: Data Metrics are messed up, everytime a new location is given, it makes that a datametric, hence using raw response to get proper data.
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[23])
            .order_by("-year")
            .first()
        )
        local_data = (
            list(local_raw_responses.data[0]["Q1"].values())[0]
            if local_raw_responses
            else None
        )
        return local_data

    def get_205_2c(self):
        """
        Note: Data Metrics are messed up, everytime a new location is given, it makes that a datametric, hence using raw response to get proper data.
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[24])
            .order_by("-year")
            .first()
        )
        local_data = (
            list(local_raw_responses.data[0]["Q1"].values())[0]
            if local_raw_responses
            else None
        )
        return local_data

    def get_205_2d(self):
        """
        Note: Data Metrics are messed up, everytime a new location is given, it makes that a datametric, hence using raw response to get proper data.
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[25])
            .order_by("-year")
            .first()
        )
        local_data = (
            list(local_raw_responses.data[0]["Q1"][0].values())[0]
            if local_raw_responses
            else None
        )
        return local_data

    def get_205_2e(self):
        """
        Note: Data Metrics are messed up, everytime a new location is given, it makes that a datametric, hence using raw response to get proper data.
        """
        local_raw_responses = (
            self.raw_responses.filter(path__slug=self.slugs[26])
            .order_by("-year")
            .first()
        )
        local_data = (
            list(local_raw_responses.data[0]["Q1"].values())[0]
            if local_raw_responses
            else None
        )
        return local_data

    def get_415_1a(self):
        self.slugs[28] = "gri-social-political_involvement-415-1-financial"
        local_data_points = self.data_points.filter(path__slug=self.slugs[28]).order_by(
            "-year"
        )
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_205_3d(self):
        slug = self.slugs[31]
        return collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=slug)
        )

    def get_api_response(self):
        response_data = dict()
        response_data["year"] = get_maximum_months_year(self.report)
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

        response_data["201_1ab"] = self.get_201_1ab()
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
        response_data["207_2b"] = self.get_207_2b()
        response_data["3_3cde"] = self.get_3_3cde()
        response_data["207_2c"] = self.get_207_2c()
        response_data["207_3a"] = self.get_207_3a()
        response_data["205_3a_anti_corruption"] = self.get_205_3a()
        response_data["205_3b_anti_corruption"] = (
            collect_data_by_raw_response_and_index(
                self.data_points.filter(path__slug=self.slugs[29])
            )
        )
        response_data["205_3c_anti_corruption"] = (
            collect_data_by_raw_response_and_index(
                self.data_points.filter(path__slug=self.slugs[30])
            )
        )
        response_data["205_3d_anti_corruption"] = self.get_205_3d()
        response_data["205_1a"] = self.get_205_1a()
        response_data["205_2a"] = self.get_205_2a()
        response_data["205_2b"] = self.get_205_2b()
        response_data["205_2c"] = self.get_205_2c()
        response_data["205_2d"] = self.get_205_2d()
        response_data["205_2e"] = self.get_205_2e()
        response_data["415_1a"] = self.get_415_1a()
        response_data["3_3cde_social"] = self.get_3_3cde()
        response_data["financial_implications-201-2a"] = (
            collect_data_by_raw_response_and_index(
                self.data_points.filter(path__slug=self.slugs[27])
            )
        )
        response_data["economic_analyse"] = {}
        response_data["economic_analyse"][
            "communication_training_analyze"
        ] = self.get_communication_training_analyze()
        response_data["economic_analyse"][
            "market_presence_analyze"
        ] = self.get_market_presence_analyze()
        response_data["economic_analyse"][
            "operations_assessed_analyze"
        ] = self.get_operations_assessed_analyze()
        response_data["205_3a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[28])
        )
        response_data["202_2a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[32])
        )
        return response_data

    def get_report_response(self):
        response_data = self.get_api_response()
        # * Convert every key in response_data from "-" to "_"
        response_data = {
            key.replace("-", "_"): value for key, value in response_data.items()
        }
        return response_data
