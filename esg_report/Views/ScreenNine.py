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
from common.utils.value_types import get_decimal
from sustainapp.utils import (
    get_ratio_of_annual_total_compensation_ratio_of_percentage_increase_in_annual_total_compensation,
)

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
            46: "gri-governance-determine-remuneration-2-20-a-process",
            47: "gri-governance-determine-remuneration-2-22-b-results",
            48: "gri-governance-policy_commitments-2-23-a-business_conduct",
            49: "gri-governance-policy_commitments-2-23-b-human_rights",
            50: "gri-governance-policy_commitments-2-23-c-links",
            51: "gri-governance-policy_commitments-2-23-c-leave",
            52: "gri-governance-policy_commitments-2-23-e-report",
            53: "gri-governance-policy_commitments-2-23-f-describe",
            54: "gri-economic-anti_competitive_behavior-206-1b-judgements",
            55: "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1a-s1",
            56: "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1b-s2",
            57: "gri-economic-ratios_of_standard_entry-202-1c-location",
            58: "gri-economic-ratios_of_standard_entry-202-1d-definition",
            59: "gri-governance-compensation_ratio-2-21-a-annual",
            60: "gri-governance-compensation_ratio-2-21-b-percentage",
        }



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
        response_data["2_21_a_analyse_governance"] = (
            self.get_2_21_a_analyse_governance()
        )
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
        response_data["2_20_a"] = self.get_2_20_a()
        response_data["2_20_b"] = self.get_2_20_b()
        response_data["206_1b"] = self.get_206_b()
        response_data["2_23_f"] = self.get_2_23_f()
        response_data["2_23_e"] = self.get_2_23_e()
        response_data["2_23_d"] = self.get_2_23_d()
        response_data["2_23_c"] = self.get_2_23_c()
        response_data["2_23_b"] = self.get_2_23_b()
        response_data["2_23_a"] = self.get_2_23_a()
        response_data["2_202_1d"] = self.get_2_202_1d()
        response_data["2_202_1c"] = self.get_2_202_1c()
        response_data["2_202_1b"] = self.get_2_202_1b()
        response_data["2_202_1a"] = self.get_2_202_1a()
        response_data["2_23_f"] = self.get_2_23_f()
        response_data["2_23_e"] = self.get_2_23_e()
        response_data["2_23_d"] = self.get_2_23_d()
        response_data["2_23_c"] = self.get_2_23_c()
        response_data["2_23_b"] = self.get_2_23_b()
        return Response(response_data, status=status.HTTP_200_OK)
