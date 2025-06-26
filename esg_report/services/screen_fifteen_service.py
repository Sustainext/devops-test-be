from esg_report.utils import (

    calling_analyse_view_with_params,
    get_management_materiality_topics,
)
from common.utils.report_datapoint_utils import get_raw_responses_as_per_report
from common.utils.report_datapoint_utils import get_data_points_as_per_report
from common.utils.get_data_points_as_raw_responses import collect_data_by_raw_response_and_index,collect_data_and_differentiate_by_location
from esg_report.Serializer.ScreenFifteenSerializer import ScreenFifteenSerializer
from django.core.exceptions import ObjectDoesNotExist
from esg_report.models.ScreenFifteen import ScreenFifteenModel
from sustainapp.models import Report


class ScreenFifteenService:
    def __init__(self, report_id, request):
        self.report = Report.objects.get(id=report_id)
        self.request = request
        self.slugs = {
            0: "gri-social-product_safety-416-1a-number",
            1: "gri-social-compliance-416-2a-total_number",
            2: "gri-social-compliance-416-2b-statement",
            3: "gri-social-product_labeling-417-1a-required",
            4: "gri-social-product_labeling-417-1b-number",
            5: "gri-social-non_compliance_labeling-417-2a-incidents",
            6: "gri-social-statement_labeling-417-2b-statement",
            7: "gri-social-non_compliance_marketing-417-3a-incidents",
            8: "gri-social-statement_marketing-417-3b-statement",
            9: "gri-social-customer_privacy-418-1b-identified_leaks",
            10: "gri-social-customer_privacy-418-1c-statement",
            11: "gri_collect_product_safety_management_material_topic",
            12: "gri_collect_marketing_and_labeling_management_material_topic",
            13: "gri_collect_customer_privacy_management_material_topic",
        }

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_api_response(self):
        response_data = {}
        try:
            screen_fifteen: ScreenFifteenModel = self.report.screen_fifteen
            serializer = ScreenFifteenSerializer(screen_fifteen)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            # * Get all the fields of ScreenFifteenModel except the report field, and ID field
            response_data.update(
                {
                    field.name: None
                    for field in ScreenFifteenModel._meta.fields
                    if field.name not in ["id", "report"]
                }
            )
        self.set_data_points()
        self.set_raw_responses()
        response_data["416_1a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0]),
        )
        response_data["416_1a_analyse"] = calling_analyse_view_with_params(
            view_url="get_customer_health_safety_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["416_2a"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[1]),
        )
        response_data["416_2b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[2]),
        )
        response_data["417_1a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[3]),
        )
        response_data["417_1b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[4]),
        )
        response_data["417_2a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[5]),
        )
        response_data["417_2b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[6]),
        )
        response_data["417_1b_analysis"] = calling_analyse_view_with_params(
            view_url="get_marketing_and_labeling_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["417_3a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[7]),
        )
        response_data["417_3b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[8]),
        )
        response_data["418_1a_analyse"] = calling_analyse_view_with_params(
            view_url="get_customer_privacy_analysis",
            request=self.request,
            report=self.report,
        )
        response_data["418_1b"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[9]),
        )
        response_data["418_1c"] = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[10]),
        )
        response_data["3-3cde_15-1-1"] = get_management_materiality_topics(
            self.report, self.slugs[11]
        )
        response_data["3-3cde_15-2-1"] = get_management_materiality_topics(
            self.report, self.slugs[12]
        )
        response_data["3-3cde_15-3-1"] = get_management_materiality_topics(
            self.report, self.slugs[13]
        )

        return response_data

    def get_report_response(self):
        response_data = self.get_api_response()
        response_data = {
            key.replace("-", "_"): value for key, value in response_data.items()
        }
        return response_data
