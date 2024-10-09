from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenNine import ScreenNine
from datametric.models import RawResponse
from esg_report.Serializer.ScreenNineSerializer import ScreenNineSerializer
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class ScreenNineView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slugs = {
            0: "gri-governance-structure-2-9-a-governance_structure",
            1: "gri-governance-structure-2-9-b-committees",
            2: "gri-governance-structure-2-9-c-composition",
            3: "gri-governance-nomination-2-10-a-nomination",
            4: "gri-governance-nomination-2-10-b-criteria",
            5: "gri-governance-nomination-2-10-b-consideration_and_selection",
            6: "gri-governance-chair_of_board-2-11-b-chair",
            7: "gri-economic-proportion_of_senior_management-local_community-202-2a",
            8: "gri-economic-proportion_of_senior_management-senior_management-202-2b",
            9: "gri-economic-proportion_of_senior_management-local-202-2c",
            10: "gri-economic-proportion_of_senior_management-operation-202-2d",
            11: "gri-governance-management_of_impact-2-12-a-senior_executives",
            12: "gri-governance-management_of_impact-2-12-b-due_diligence",
            13: "gri-governance-sustainability_knowledge-2-17-a",
            14: "gri-governance-sustainability_reporting-2-14-role",
            15: "gri-governance-delegation-2-13-a-managing",
            16: "gri-governance-delegation-2-13-b-frequency",
            17: "gri-governance-critical_concerns-2-16-a-critical_concerns",
            18: "gri-governance-critical_concerns-2-16-b-report",
            19: "gri-governance-performance_evaluations-2-18-a-processes",
            20: "gri-governance-performance_evaluations-2-18-b-evaluation",
            21: "gri-governance-performance_evaluations-2-18-c-actions",
            22: "gri-governance-remuneration-2-19-a-remuneration",
            23: "gri-governance-compensation_ratio-2-21-a-annual",
            24: "gri-governance-compensation_ratio-2-21-b-percentage",
            25: "gri-governance-compensation_ratio-2-21-c-contextual",
            26: "gri-governance-sustainability_strategy-2-22-a_provide",
            27: "gri-governance-process-2-25-a-commitments",
            28: "gri-governance-process-2-25-b-approach",
            29: "gri-governance-process-2-25-c-other_processes",
            30: "gri-governance-process-2-25-d-stakeholders",
            31: "gri-governance-process-2-25-e-effectiveness",
            32: "gri-governance-advice_and_concerns-2-26-a",
            33: "gri-general-laws_and_regulation-instance-2-27-a",
            34: "gri-general-laws_and_regulation-monetary-2-27-b",
            35: "gri-general-laws_and_regulation-significant-2-27-c",
            36: "gri-general-laws_and_regulation-organization-2-27-d",
            37: "gri-economic-anti_competitive_behavior-206-1a-behavior",
            38: "gri-economic-defined_benefit_plan-general-201-3a",
            39: "gri-economic-defined_benefit_plan-separate-201-3b",
            40: "gri-economic-defined_benefit_plan-explain-201-3c",
            41: "gri-economic-defined_benefit_plan-percentage-201-3d",
            42: "gri-economic-defined_benefit_plan-mention-201-3e",
            43: "gri-governance-conflict_of_interest-2-15-a-highest",
            44: "gri-governance-conflict_of_interest-2-15-b-report",
            45: "gri-general-membership_association-2-28-a-report",
        }

    def set_raw_responses(self):
        self.raw_responses = (
            RawResponse.objects.filter(path__slug__in=list(self.slugs.values()))
            .filter(client=self.report.client)
            .filter(Q(organization=self.report.organization))
        )

    def get_2_9_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[0])
            .order_by("-year")
            .first()
        )
        return raw_response.data[0].get("Q1") if raw_response is not None else None

    def get_2_9_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[1])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        if data is None:
            return data
        else:
            d = dict()
            for index, list_item in enumerate(data):
                d[index] = list_item
            return d

    def get_2_9_c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[2])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0] if raw_response is not None else None
        return data

    def get_2_10_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[3])
            .order_by("-year")
            .first()
        )
        data = (
            raw_response.data[0].get("Q1").get("Q1")
            if raw_response is not None
            else None
        )
        return data

    def get_2_10_b(self):
        def get_2_10_b_criteria():
            raw_response = (
                self.raw_responses.filter(path__slug=self.slugs[4])
                .order_by("-year")
                .first()
            )
            data = raw_response.data[0].get("Q1") if raw_response is not None else None
            return data

        def get_2_10_b_governance_body_nomination_criteria():
            raw_response = (
                self.raw_responses.filter(path__slug=self.slugs[5])
                .order_by("-year")
                .first()
            )
            data = raw_response.data if raw_response is not None else None
            return data

        data = {}
        data["criteria"] = get_2_10_b_criteria()
        data["governance_body_nomination_criteria"] = (
            get_2_10_b_governance_body_nomination_criteria()
        )
        return data

    def get_2_11_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[6])
            .order_by("-year")
            .first()
        )
        local_response_data = raw_response.data[0] if raw_response is not None else None
        if not local_response_data:
            return local_response_data
        else:
            if local_response_data.get("Q2") == "No":
                return "No"
            else:
                return local_response_data.get("Q3")

    def get_202_2a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[7])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_202_2b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[8])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_202_2c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[9])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_202_2d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[10])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_12_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[11])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0] if raw_response is not None else None
        return data

    def get_2_12_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[12])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0] if raw_response is not None else None
        return data

    def get_2_17_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[13])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_14_a_and_b(self):
        data = {}
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[14])
            .order_by("-year")
            .first()
        )
        response_data = raw_response.data[0] if raw_response is not None else None
        if not response_data:
            return response_data

        data["highest_body_approves_report"] = response_data.get("Q1")
        data["reason_for_yes"] = response_data["Q2"]
        data["reason_for_no"] = response_data["Q3"]
        return data

    def get_2_13_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[15])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {
            "governance_body_responsibility_delegation": raw_response_data.get("Q1"),
            "has_appointed_executive_for_impact_management": raw_response_data["Q2"],
            "reason_for_has_appointed_executive_for_impact_management": raw_response_data[
                "Q3"
            ],
            "has_delegated_impact_management_to_employees": raw_response_data["Q4"],
            "reason_for_has_delegated_impact_management_to_employees": raw_response_data[
                "Q5"
            ],
        }
        return data

    def get_2_13_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[16])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_16_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[17])
            .order_by("-year")
            .first()
        )
        response_data = raw_response.data[0] if raw_response is not None else None
        if not response_data:
            return response_data
        data = {}
        data["critical_concerns_communicated_to_governance_body"] = response_data.get(
            "Q1"
        )
        data["critical_concerns_communication_description"] = response_data["Q2"]
        return data

    def get_2_16_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[18])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["total_critical_concerns_reported"] = raw_response_data.get("Q1")
        data["nature_of_critical_concerns_reported"] = raw_response_data["Q2"]
        return data

    def get_2_18_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[19])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_18_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[20])
            .order_by("-year")
            .first()
        )
        response_data = raw_response.data[0] if raw_response is not None else None
        if not response_data:
            return response_data
        data = {}
        data["evaluations_independent"] = response_data["Q2"]
        data["evaluation_frequency"] = response_data["Q3"]
        return data

    def get_2_18_c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[21])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_19_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[22])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["remuneration_policy_fixed_and_variable_pay"] = raw_response_data.get("Q1")
        data["remuneration_policy_sign_on_bonuses"] = raw_response_data["Q2"]
        data["remuneration_policy_termination_payments"] = raw_response_data["Q3"]
        data["remuneration_policy_clawbacks"] = raw_response_data["Q4"]
        data["remuneration_policy_retirement_benefits"] = raw_response_data["Q5"]
        return data

    def get_2_21_a(self):
        # TODO: Sum of annual total compensation ratio
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[23])
            .order_by("-year")
            .first()
        )
        # TODO: Verify the logic to be used for multiple locations.
        data = raw_response.data[0] if raw_response is not None else None
        return data

    def get_2_21_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[24])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0] if raw_response is not None else None
        return data

    def get_2_21_c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[25])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_22_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[26])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_28_a(self):
        # TODO: Finish this function to return the correct data
        raw_response = (
            (self.raw_responses.filter(path__slug=self.slugs[45]))
            .order_by("-year")
            .first()
        )
        local_data = raw_response.data if raw_response is not None else None
        if not local_data:
            return local_data
        else:
            return local_data[0]["MembershipAssociations"]["MembershipAssociations"]

    def get_2_25_data(self):
        data = {}
        for i in range(27, 32):
            slug = self.slugs[i]
            raw_response = (
                self.raw_responses.filter(path__slug=slug).order_by("-year").first()
            )
            key = f"2_25_{chr(97 + i - 27)}"  # This will generate keys 2_25_a, 2_25_b, etc.
            data[key] = (
                raw_response.data[0].get("Q1") if raw_response is not None else None
            )
        return data

    def get_2_26_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[32])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["responsible_business_conduct_advice"] = raw_response_data.get("Q1")
        data["business_conduct_concerns"] = raw_response_data["Q2"]
        return data

    def get_2_27_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[33])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["significant_non_compliance_occurred"] = raw_response_data.get("Q1")
        data["total_significant_non_compliance_instances"] = raw_response_data["Q2"]
        data["total_fines_incurred_instances"] = raw_response_data.get("Q3")
        data["total_non_monetary_sanctions_instances"] = raw_response_data.get("Q4")

        return data

    def get_2_27_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[34])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["total_fines_incurred_instances"] = raw_response_data.get("Q1")
        data["total_fines_incurred_instances_previous_periods"] = raw_response_data[
            "Q2"
        ]
        return data

    def get_2_27_c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[35])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_27_d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[36])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_3_c_d_e_in_material_topics(self):
        # TODO: Complete this after completing logic of selection material topic for report.
        return None

    def get_206_1a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[37])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["legal_actions_anti_competitive_behavior"] = raw_response_data.get("Q1")
        data["number_legal_actions_anti_competitive_behavior"] = {}
        data["number_legal_actions_anti_competitive_behavior"]["pending"] = (
            raw_response_data["Q2"]
        )
        data["number_legal_actions_anti_competitive_behavior"]["completed"] = (
            raw_response_data["Q3"]
        )
        data["number_antitrust_monopoly_violations"] = raw_response_data["Q4"]
        return data

    def get_201_3a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[38])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_201_3b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[39])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["liabilities_coverage_extent"] = raw_response_data.get("Q1")
        data["liabilities_estimate_basis"] = raw_response_data["Q2"]
        data["liabilities_estimate_date_details"] = raw_response_data["Q3"]
        return data

    def get_201_3c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[40])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {}
        data["strategy_for_full_pension_liabilities_coverage"] = raw_response_data.get(
            "Q1"
        )
        data["timescale_for_full_pension_liabilities_coverage"] = raw_response_data[
            "Q2"
        ]
        return data

    def get_201_3d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[41])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_201_3e(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[42])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_15_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[43])
            .order_by("-year")
            .first()
        )
        data = raw_response.data[0].get("Q1") if raw_response is not None else None
        return data

    def get_2_15_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[44])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        data = {
            "cross_board_membership": raw_response_data[0]["Disclosed"],
            "cross_shareholding_with_suppliers_and_other_stakeholders": raw_response_data[
                1
            ][
                "Disclosed"
            ],
            "existence_of_controlling_shareholders": raw_response_data[2]["Disclosed"],
            "related_parties_theri_relationships_transactions_and_outstanding_balances": raw_response_data[
                3
            ][
                "Disclosed"
            ],
            "others": raw_response_data[4]["Disclosed"],
        }
        return data

    def put(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ScreenNineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            screen_nine = self.report.screen_nine
            screen_nine.delete()
        except ObjectDoesNotExist:
            # * If the screen_nine does not exist, create a new one
            pass
        serializer.save(report=self.report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, report_id):
        # TODO: Apply this optimisation in self.raw_responses. (https://chatgpt.com/share/66fd7656-1684-8008-b95e-b3b26ccb1aae)
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_nine = self.report.screen_nine
            serializer = ScreenNineSerializer(screen_nine)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            pass
        self.set_raw_responses()
        response_data["2_9_a"] = self.get_2_9_a()
        response_data["2_9_b"] = self.get_2_9_b()
        response_data["2_9_c"] = self.get_2_9_c()
        response_data["2_10_a"] = self.get_2_10_a()
        response_data["2_10_b"] = self.get_2_10_b()
        response_data["2_11_b"] = self.get_2_11_b()
        response_data["202_2a"] = self.get_202_2a()
        response_data["202_2b"] = self.get_202_2b()
        response_data["202_2c"] = self.get_202_2c()
        response_data["202_2d"] = self.get_202_2d()
        response_data["2_12_a"] = self.get_2_12_a()
        response_data["2_12_b"] = self.get_2_12_b()
        response_data["2_17_a"] = self.get_2_17_a()
        response_data["2_14_a_and_b"] = self.get_2_14_a_and_b()
        response_data["2_13_a"] = self.get_2_13_a()
        response_data["2_13_b"] = self.get_2_13_b()
        response_data["2_16_a"] = self.get_2_16_a()
        response_data["2_16_b"] = self.get_2_16_b()
        response_data["2_18_a"] = self.get_2_18_a()
        response_data["2_18_b"] = self.get_2_18_b()
        response_data["2_18_c"] = self.get_2_18_c()
        response_data["2_19_a"] = self.get_2_19_a()
        response_data["2_21_a"] = self.get_2_21_a()
        response_data["2_21_b"] = self.get_2_21_b()
        response_data["2_21_c"] = self.get_2_21_c()
        response_data["2_22_a"] = self.get_2_22_a()
        response_data["2_28_a"] = self.get_2_28_a()
        response_data["2_25_data"] = self.get_2_25_data()
        response_data["2_26_a"] = self.get_2_26_a()
        response_data["2_27_a"] = self.get_2_27_a()
        response_data["2_27_b"] = self.get_2_27_b()
        response_data["2_27_c"] = self.get_2_27_c()
        response_data["2_27_d"] = self.get_2_27_d()
        response_data["3_c_d_e_in_material_topics"] = (
            self.get_3_c_d_e_in_material_topics()
        )
        response_data["206_1a"] = self.get_206_1a()
        response_data["201_3a"] = self.get_201_3a()
        response_data["201_3b"] = self.get_201_3b()
        response_data["201_3c"] = self.get_201_3c()
        response_data["201_3d"] = self.get_201_3d()
        response_data["201_3e"] = self.get_201_3e()
        response_data["2_15_a"] = self.get_2_15_a()
        response_data["2_15_b"] = self.get_2_15_b()
        return Response(response_data, status=status.HTTP_200_OK)
