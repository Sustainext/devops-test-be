from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenTen import ScreenTen
from materiality_dashboard.models import ManagementApproachQuestion
from datametric.models import RawResponse, DataMetric, DataPoint
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_maximum_months_year,
    collect_data_by_raw_response_and_index,
    get_management_materiality_topics,
)
from esg_report.Serializer.ScreenTenSerializer import ScreenTenSerializer
from sustainapp.models import Report
from sustainapp.Utilities.supplier_environment_analyse import (
    new_suppliers,
    calculate_percentage,
)
from sustainapp.Utilities.supplier_social_assessment_analyse import (
    get_social_data,
    get_pos_data,
    get_data,
    filter_non_zero_values,
)
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from logging import getLogger

logger = getLogger("error.log")

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
            8: "gri-supplier_environmental_assessment-new_suppliers-308-1a",
            9: "gri-supplier_environmental_assessment-negative_environmental-308-2d",
            10: "gri-supplier_environmental_assessment-negative_environmental-308-2e",
            11: "gri-economic-proportion_of_spending_on_local_suppliers-percentage-204-1a",
            12: "gri-supplier_environmental_assessment-negative_environmental-308-2e",
            13: "gri-social-supplier_screened-414-1a-number_of_new_suppliers",
            14: "gri-social-impacts_and_actions-414-2b-number_of_suppliers",
            15: "gri_collect_supplier_environmental_assessment_management_material_topic",
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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(report=self.report)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(report=self.report)

    def get_414_2b_collect(self):
        local_data_points = self.data_points.filter(
            path__slug=self.slugs[14]
        ).select_related("data_metric")
        return collect_data_by_raw_response_and_index(local_data_points)

    def get_414_1a_collect(self):
        local_data_points = self.data_points.filter(
            path__slug=self.slugs[13]
        ).select_related("data_metric")
        response_data = {}
        for dp in local_data_points:
            response_data[dp.data_metric.name] = dp.value
        return response_data

    def get_414_1a_analyse(self):
        year = get_maximum_months_year(self.report)
        dp, pos = {}, {}
        filter_by = {}

        if self.report.corporate:
            filter_by["corporate"] = self.report.corporate
        elif self.report.organization:
            filter_by["organization"] = self.report.organization

        if filter_by:
            dp_data, pos_data = get_data(
                year=get_maximum_months_year(self.report),
                client_id=self.report.user.client.id,
                filter_by=filter_by,
            )
            dp = get_social_data(dp_data)
            pos = get_pos_data(pos_data)

        final = {
            "new_suppliers_that_were_screened_using_social_criteria": filter_non_zero_values(
                dp
            ),
            "negative_social_impacts_in_the_supply_chain_and_actions_taken": filter_non_zero_values(
                pos
            ),
        }
        return final

    def get_308_2e_collect(self):
        local_data_points = self.data_points.filter(
            path__slug=self.slugs[12]
        ).select_related("data_metric")
        response_data = {}
        for dp in local_data_points:
            response_data[dp.data_metric.name] = dp.value
        return response_data

    def get_308_2de_analyse(self):
        year = get_maximum_months_year(self.report)
        self.client_id = self.request.user.client.id
        filter_by = {}
        filter_by["organization__id"] = self.report.organization.id
        if self.report.corporate is not None:
            filter_by["corporate__id"] = self.report.corporate.id
        else:
            filter_by["corporate__id"] = None
        supplier_env_data = {}
        supplier_env_data["gri_308_1a"] = new_suppliers(
            org=self.report.organization,
            corp=self.report.corporate,
            client_id=self.report.user.client.id,
            year=year,
            path=self.slugs[8],
            filter_by=filter_by,
        )
        supplier_env_data["gri_308_2d"] = new_suppliers(
            org=self.report.organization,
            corp=self.report.corporate,
            client_id=self.report.user.client.id,
            year=year,
            path=self.slugs[9],
            filter_by=filter_by,
        )
        supplier_env_data["gri_308_2e"] = new_suppliers(
            org=self.report.organization,
            corp=self.report.corporate,
            client_id=self.report.user.client.id,
            year=year,
            path=self.slugs[10],
            filter_by=filter_by,
        )
        return supplier_env_data

    def get_204_1abc_using_datapoint(self) -> dict[str, Any]:
        """
        Gives data for multiple locations.
        """
        slug = self.slugs[11]
        data_points = self.data_points.filter(path__slug=slug).order_by("-year")
        data_metrics = DataMetric.objects.filter(path__slug=slug)
        response_data = {}
        for data_metric in data_metrics:
            response_data[data_metric.name] = {}
            for data_point in data_points:
                response_data[data_metric.name][
                    data_point.locale.name
                ] = data_point.value
        return response_data

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
        raw_responses = (self.raw_responses.filter(path__slug=self.slugs[3])).order_by(
            "-year"
        )
        if raw_responses.exists():
            response_data["204-1c"] = raw_responses.first().data[0]["Q1"]
        else:
            response_data["204-1c"] = None

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
        local_data = raw_responses.first().data[0] if raw_responses.exists() else {}
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

    # def get_3_c_d_e_in_material_topics(self):
    #     try:
    #         dps = self.data_points.filter(
    #             path__slug=self.slugs[15],
    #             corporate=self.report.corporate,
    #             organization=self.report.organization,
    #             locale=None,
    #         ).order_by("-year")
    #         data = {
    #             "economic_governance": {
    #                 "GRI33cd": "",
    #                 "GRI33e": "",
    #             }
    #         }
    #         for dps_data in dps:
    #             if dps_data.metric_name == "GRI33cd":
    #                 data["economic_governance"]["GRI33cd"] = dps_data.value
    #             elif dps_data.metric_name == "GRI33e":
    #                 data["economic_governance"]["GRI33e"] = dps_data.value
    #         return data
    #     except Exception as e:
    #         logger.error(
    #             f"An error occured while getting 3_c_d_e_in_material_topics : {e}"
    #         )

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
        self.set_data_points()
        materiality_assessment = get_materiality_assessment(self.report)
        if materiality_assessment is None:
            management_approach_question = None
        else:
            management_approach_question: ManagementApproachQuestion | None = (
                ManagementApproachQuestion.objects.filter(
                    assessment=materiality_assessment
                ).first()
            )
        response_data["3-3cde"] = {}
        if management_approach_question:
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
        response_data.update(self.get_308_2de_analyse())
        response_data["308_2e_collect"] = self.get_308_2e_collect()
        response_data["414_1a_collect"] = self.get_414_1a_collect()
        response_data["414_1a_analyse"] = self.get_414_1a_analyse()
        response_data["414_2b_collect"] = self.get_414_2b_collect()
        response_data["3_c_d_e_in_material_topics"] = get_management_materiality_topics(
            self.report, self.slugs[15]
        )

        return Response(response_data, status=status.HTTP_200_OK)
