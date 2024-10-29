from typing import Any, Dict
from django.core.exceptions import ObjectDoesNotExist
from sustainapp.models import Report
from esg_report.models.ScreenTen import ScreenTen
from esg_report.Serializer.ScreenTenSerializer import ScreenTenSerializer
from materiality_dashboard.models import ManagementApproachQuestion
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_maximum_months_year,
    collect_data_by_raw_response_and_index,
)
from sustainapp.Utilities.supplier_environment_analyse import new_suppliers
from sustainapp.Utilities.supplier_social_assessment_analyse import (
    get_social_data,
    get_pos_data,
    get_data,
    filter_non_zero_values,
)
from datametric.models import DataMetric


class ScreenTenService:
    slugs = {
        1: "gri-economic-proportion_of_spending_on_local_suppliers-percentage-204-1a",
        2: "gri-economic-proportion_of_spending_on_local_suppliers-organization-204-1b",
        3: "gri-economic-proportion_of_spending_on_local_suppliers-definition-204-1c",
        4: "gri-social-supplier_screened-414-1a-number_of_new_suppliers",
        5: "gri-social-impacts_and_actions-414-2a-2d-2e-negative_social_impacts",
        6: "gri-social-impacts_and_actions-414-2b-number_of_suppliers",
        7: "gri-social-impacts_and_actions-414-2c-significant_actual",
        8: "gri-supplier_environmental_assessment-new_suppliers-308-1a",
        9: "gri-supplier_environmental_assessment-negative_environmental-308-2d",
        10: "gri-supplier_environmental_assessment-negative_environmental-308-2e",
        11: "gri-economic-proportion_of_spending_on_local_suppliers-percentage-204-1a",
        12: "gri-supplier_environmental_assessment-negative_environmental-308-2e",
        13: "gri-social-supplier_screened-414-1a-number_of_new_suppliers",
        14: "gri-social-impacts_and_actions-414-2b-number_of_suppliers",
    }

    @staticmethod
    def get_screen_ten(report_id: int) -> Dict[str, Any]:
        response_data = {}

        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise ObjectDoesNotExist("Report not found")

        raw_responses = get_raw_responses_as_per_report(report=report)
        data_points = get_data_points_as_per_report(report=report)

        # Serialize and update ScreenTen data
        try:
            screen_ten = report.screen_ten
            response_data.update(ScreenTenSerializer(screen_ten).data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    "company_sustainability_statement": None,
                    "approach_for_sustainability": None,
                    "sustainability_goals": None,
                    "approach_to_supply_chain_sustainability": None,
                }
            )

        response_data["3-3cde"] = ScreenTenService.get_management_approach_data(report)

        response_data.update(ScreenTenService.get_204_1abc(raw_responses))
        response_data.update(ScreenTenService.get_404_1abc(raw_responses))
        response_data.update(ScreenTenService.get_404_2abc(raw_responses))
        response_data.update(
            ScreenTenService.get_308_2de_analyse(report, raw_responses)
        )
        response_data["308_2e_collect"] = ScreenTenService.get_308_2e_collect(
            data_points
        )
        response_data["414_1a_collect"] = ScreenTenService.get_414_1a_collect(
            data_points
        )
        response_data["414_1a_analyse"] = ScreenTenService.get_414_1a_analyse(report)
        response_data["414_2b_collect"] = ScreenTenService.get_414_2b_collect(
            data_points
        )

        return response_data

    @staticmethod
    def get_management_approach_data(report):
        materiality_assessment = get_materiality_assessment(report)
        response = {
            "negative_impact_involvement_description": None,
            "stakeholder_engagement_effectiveness_description": None,
        }

        if materiality_assessment:
            management_approach = ManagementApproachQuestion.objects.filter(
                assessment=materiality_assessment
            ).first()
            if management_approach:
                response["negative_impact_involvement_description"] = (
                    management_approach.negative_impact_involvement_description
                )
                response["stakeholder_engagement_effectiveness_description"] = (
                    management_approach.stakeholder_engagement_effectiveness_description
                )

        return response

    @staticmethod
    def get_204_1abc(raw_responses):
        response_data = {}
        slugs = ScreenTenService.slugs

        for key, label in {"204-1a": 1, "204-1b": 2, "204-1c": 3}.items():
            raw_response = (
                raw_responses.filter(path__slug=slugs[label]).order_by("-year").first()
            )
            response_data[key] = raw_response.data[0]["Q1"] if raw_response else None
        return response_data

    @staticmethod
    def get_404_1abc(raw_responses):
        response_data = {}
        raw_response = (
            raw_responses.filter(path__slug=ScreenTenService.slugs[4])
            .order_by("-year")
            .first()
        )

        response_data["414-1a"] = {
            "number_of_new_suppliers_that_were_screened_using_social_criteria": (
                raw_response.data[0]["Q1"] if raw_response else None
            ),
            "total_number_of_suppliers": (
                raw_response.data[0]["Q2"] if raw_response else None
            ),
        }
        return response_data

    @staticmethod
    def get_404_2abc(raw_responses):
        response_data = {}
        raw_response_a = (
            raw_responses.filter(path__slug=ScreenTenService.slugs[5])
            .order_by("-year")
            .first()
        )
        response_data["414-2a"] = {
            "total_suppliers_terminated_negative_impact": (
                raw_response_a.data[0].get("Q1") if raw_response_a else None
            ),
            "total_suppliers_improved_negative_impact": (
                raw_response_a.data[0].get("Q2") if raw_response_a else None
            ),
            "total_suppliers_assessed_social_impact": (
                raw_response_a.data[0].get("Q3") if raw_response_a else None
            ),
        }

        raw_response_b = (
            raw_responses.filter(path__slug=ScreenTenService.slugs[6])
            .order_by("-year")
            .first()
        )
        response_data["414-2b"] = raw_response_b.data if raw_response_b else None

        raw_response_c = (
            raw_responses.filter(path__slug=ScreenTenService.slugs[7])
            .order_by("-year")
            .first()
        )
        response_data["414-2c"] = (
            raw_response_c.data[0]["Q1"] if raw_response_c else None
        )
        return response_data

    @staticmethod
    def get_308_2de_analyse(report, raw_responses):
        year = get_maximum_months_year(report)
        client_id = report.user.client.id
        filter_by = {
            "organization__id": report.organization.id,
            "corporate__id": report.corporate.id if report.corporate else None,
        }
        slugs = ScreenTenService.slugs
        return {
            "gri_308_1a": new_suppliers(
                report.organization,
                report.corporate,
                client_id,
                year,
                slugs[8],
                filter_by,
            ),
            "gri_308_2d": new_suppliers(
                report.organization,
                report.corporate,
                client_id,
                year,
                slugs[9],
                filter_by,
            ),
            "gri_308_2e": new_suppliers(
                report.organization,
                report.corporate,
                client_id,
                year,
                slugs[10],
                filter_by,
            ),
        }

    @staticmethod
    def get_308_2e_collect(data_points):
        points = data_points.filter(
            path__slug=ScreenTenService.slugs[12]
        ).select_related("data_metric")
        return {dp.data_metric.name: dp.value for dp in points}

    @staticmethod
    def get_414_1a_collect(data_points):
        points = data_points.filter(
            path__slug=ScreenTenService.slugs[13]
        ).select_related("data_metric")
        return {dp.data_metric.name: dp.value for dp in points}

    @staticmethod
    def get_414_1a_analyse(report):
        year = get_maximum_months_year(report)
        filter_by = {}
        if report.corporate:
            filter_by["corporate"] = report.corporate
        elif report.organization:
            filter_by["organization"] = report.organization

        if filter_by:
            dp_data, pos_data = get_data(year, report.user.client.id, filter_by)
            dp = get_social_data(dp_data)
            pos = get_pos_data(pos_data)

            return {
                "new_suppliers_that_were_screened_using_social_criteria": filter_non_zero_values(
                    dp
                ),
                "negative_social_impacts_in_the_supply_chain_and_actions_taken": filter_non_zero_values(
                    pos
                ),
            }
        return {}

    @staticmethod
    def get_414_2b_collect(data_points):
        points = data_points.filter(
            path__slug=ScreenTenService.slugs[14]
        ).select_related("data_metric")
        return collect_data_by_raw_response_and_index(points)
