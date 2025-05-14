from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_management_materiality_topics,
)
from sustainapp.utils import (
    get_ratio_of_annual_total_compensation_ratio_of_percentage_increase_in_annual_total_compensation,
)
from esg_report.models.ScreenNine import ScreenNine
from esg_report.Serializer.ScreenNineSerializer import ScreenNineSerializer
from django.core.exceptions import ObjectDoesNotExist
from logging import getLogger

logger = getLogger("error.log")


# TODO: Add the logic to get the data from the raw responses
class ScreenNineService:
    def __init__(self, report_id: int) -> None:
        self.report_id = report_id
        self.report = Report.objects.get(id=report_id)

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
            61: "gri_collect_economic_governance_management_material_topic",
            62: "gri-governance-remuneration-2-19-b-policies",
            63: "gri-economic-public_legal_cases-205-3d",

        }

    def get_screen_nine_data(self):
        try:
            screen_nine = self.report.screen_nine
            serializer = ScreenNineSerializer(screen_nine)
            return serializer.data
        except ObjectDoesNotExist:
            # * get all fields of ScreenNine in a dictionary
            screen_nine_data = dict()
            for field in ScreenNine._meta.fields:
                screen_nine_data[field.name] = None
            return screen_nine_data

    def get_response(self):
        self.set_raw_responses()
        response_data = dict()
        response_data.update(self.get_screen_nine_data())
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
        response_data["2_19_b"] = self.get_2_19_b()
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
        response_data["205_3d"] = self.get_205_3d()
        return response_data

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(report=self.report)

    def get_2_202_1d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[58])
            .order_by("-year")
            .first()
        )
        raw_response_data = (
            raw_response.data[0]["Q1"] if raw_response is not None else None
        )
        return raw_response_data

    def get_2_202_1c(self):
        """
        [
                {
                        "Currency": "100 USD",
                        "Locationofoperation": {
                                "currencyValue": "",
                                "locations": [
                                        {
                                                "id": 1,
                                                "value": "Rajendra Nagar"
                                        }
                                ],
                                "radioValue": "Yes",
                                "wages": {}
                        }
                }
        ]
        """
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[57])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        return raw_response_data

    def get_2_202_1b(self):
        """
        [
                        {
                                "Q1": "Yes",
                                "Q2": "Yes",
                                "Q3": "Something"
                        }
        ]
        """
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[56])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        else:
            data = {
                "does_your_organisation_subject_to_minimum_wage_rules": raw_response_data.get(
                    "Q1"
                ),
                "are_a_significant_proportion_of_other_workers_excluding_employees_performing_the_organizations_activities_compensated_based_on_wages_subject_to_minimum_wage_rules": raw_response_data.get(
                    "Q2"
                ),
                "describe_the_actions_taken_to_determine_whether_these_workers_are_paid_above_the_minimum_wage": raw_response_data.get(
                    "Q3"
                ),
            }
            return data

    def get_2_202_1a(self):
        """
        [
            {
                "Q1": "Yes",
                "Q2": "Yes",
                "Q3": "USD",
                "Q4": [
                    {
                        "Female": "101",
                        "Location": "Rajendra Nagar",
                        "Male": "100",
                        "Non-binary": "102"
                    }
                ]
            }
            ]
        """
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[55])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        else:
            data = {
                "does_your_organisation_subject_to_minimum_wage_rules": raw_response_data.get(
                    "Q1"
                ),
                "are_a_significant_proportion_of_employees_compensated_based_on_wages_subject_to_minimum_wage_rules": raw_response_data.get(
                    "Q2"
                ),
                "currency": raw_response_data.get("Q3"),
                "if_yes_then_specify_the_relevant_entry_level_wage_by_gender_at_significant_locations_of_operation_to_the_minimum_wage": raw_response_data.get(
                    "Q4"
                ),
            }
            return data

    def get_206_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[54])
            .order_by("-year")
            .first()
        )
        data = raw_response.data if raw_response is not None else None
        return data

    def get_2_23_f(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[53])
            .order_by("-year")
            .first()
        )
        raw_response_data = (
            raw_response.data[0]["Q1"] if raw_response is not None else None
        )
        return raw_response_data

    def get_2_23_e(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[52])
            .order_by("-year")
            .first()
        )
        raw_response_data = (
            raw_response.data[0]["Q1"] if raw_response is not None else None
        )
        return raw_response_data

    def get_2_23_d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[51])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data if raw_response is not None else None
        return raw_response_data

    def get_2_23_c(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[50])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        else:
            data = {
                "are_the_organizations_policy_commitments_publicly_available": raw_response_data[
                    0
                ]["Q1"],
                "please_provide_links_to_the_policy_commitments": raw_response_data[0][
                    "Q2"
                ],
                "policy commitments are not publicly available": raw_response_data[0][
                    "Q3"
                ],
            }
            return data

    def get_2_23_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[49])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data if raw_response is not None else None
        if not raw_response_data:
            return raw_response_data
        
        else:
            data = {
                "the_internationally_recognized_human_rights_that_the_commitment_covers": raw_response_data[
                    0
                ]["Disclosed"],
                "the_categories_of_stakeholders_including_at_risk_or_vulnerable_groups_that_the_organization_gives_particular_attention_to_in_the_commitment": raw_response_data[
                    1
                ]["Disclosed"],
            }
            return data

    def get_2_23_a(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[48])
            .order_by("-year")
            .first()
        )
        data = raw_response.data if raw_response is not None else None
        return data

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
        d = {}
        if not local_response_data:
            return local_response_data
        else:
            if local_response_data.get("Q2") == "No":
                d["is_chair_of_highest_governance"] = "No"
            else:
                d["is_chair_of_highest_governance"] = local_response_data.get("Q2")
                d["table"] = local_response_data["Q3"][0]
        return d

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
        try:
            data = raw_response.data[0] if raw_response is not None else None
        except IndexError:
            data = None
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
    
    def get_2_19_b(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[62])
            .order_by("-year")
            .first()
        )
        raw_response_data = raw_response.data[0] if raw_response is not None else None
        return raw_response_data


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

    def get_2_21_a_analyse_governance(self):
        ...
        local_slugs = {
            0: self.slugs[59],
            1: self.slugs[60],
        }
        return get_ratio_of_annual_total_compensation_ratio_of_percentage_increase_in_annual_total_compensation(
            raw_response=self.raw_responses, slugs=local_slugs
        )

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
        return get_management_materiality_topics(self.report, self.slugs[61])

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
            ]["Disclosed"],
            "existence_of_controlling_shareholders": raw_response_data[2]["Disclosed"],
            "related_parties_theri_relationships_transactions_and_outstanding_balances": raw_response_data[
                3
            ]["Disclosed"],
            "others": raw_response_data[4]["Disclosed"],
        }
        return data

    def get_2_20_a(self):
        local_raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[46])
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data if local_raw_response is not None else None
        if not local_data:
            return local_data
        return local_data[0]

    def get_2_20_b(self):
        local_raw_response = (
            RawResponse.objects.filter(
                path__slug=self.slugs[47]
            )  # * This is the correct path.
            .order_by("-year")
            .first()
        )
        local_data = local_raw_response.data if local_raw_response is not None else None
        if not local_data:
            return local_data
        else:
            return local_data[0]["Q1"]

    def get_205_3d(self):
        raw_response = (
            self.raw_responses.filter(path__slug=self.slugs[63])
            .order_by("-year")
            .first()
        )
        return raw_response.data[0] if raw_response is not None else None
