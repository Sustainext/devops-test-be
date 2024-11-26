from sustainapp.models import Report
from esg_report.models.ScreenTwelve import ScreenTwelve
from collections import defaultdict
from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    get_data_by_raw_response_and_index,
    forward_request_with_jwt,
    get_emission_analysis_as_per_report,
)
from datametric.utils.analyse import set_locations_data
from sustainapp.Utilities.emission_analyse import (
    get_top_emission_by_scope,
    calculate_scope_contribution,
)
from sustainapp.Views.MaterialAnalyse import GetMaterialAnalysis
from sustainapp.Views.Analyse.WaterAnalyse import WaterAnalyse
from sustainapp.Views.EnergyAnalyse import EnergyAnalyzeView
from sustainapp.Views.WasteAnalyse import GetWasteAnalysis
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenTwelveSerializer import ScreenTwelveSerializer
from common.utils.value_types import format_decimal_places


class ScreenTwelveService:
    def __init__(self, report_id, request):
        self.report = Report.objects.get(id=report_id)
        self.request = request
        self.slugs = {
            0: "gri-environment-emissions-301-a-scope-1",
            1: "gri-environment-emissions-301-a-scope-2",
            2: "gri-environment-emissions-301-a-scope-3",
            3: "gri-environment-materials-301-1a-non_renewable_materials",
            4: "gri-environment-materials-301-1a-renewable_materials",
            5: "gri-environment-materials-301-2a-recycled_input_materials",
            6: "gri-environment-materials-301-3a-3b-reclaimed_products",
            7: "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas",
            8: "gri-environment-energy-302-1a-1b-direct_purchased",
            9: "gri-environment-energy-302-1c-1e-consumed_fuel",
            10: "gri-environment-energy-302-1-self_generated",
            11: "gri-environment-energy-302-1d-energy_sold",
            12: "gri-environment-energy-302-1f-2b-4d-5c-smac",
            13: "gri-environment-energy-302-1g-2c-conversion_factor",
            14: "gri-environment-energy-302-2a-energy_consumption_outside_organization",
            15: "gri-environment-energy-302-2b-smac",
            16: "gri-environment-energy-302-2c-conversion_factor",
            17: "gri-environment-energy-302-3a-3b-3c-3d-energy_intensity",
            18: "gri-environment-energy-302-4a-4b-reduction_of_energy_consumption",
            19: "gri-environment-energy-302-4c-base_year_or_baseline",
            20: "gri-environment-energy-302-4d-smac",
            21: "gri-environment-energy-302-5a-5b-reduction_in_energy_in_products_and_servies",
            22: "gri-environment-energy-302-5b-base_year_or_baseline",
            23: "gri-environment-energy-302-5c-smac",
            24: "gri-environment-waste-306-1-significant_waste",
            25: "gri-environment-waste-306-3a-3b-waste_generated",
            26: "gri-environment-waste-306-3b-contextual_info",
            27: "gri-environment-waste-306-2-management_of_significant_waste",
            28: "gri-environment-waste-306-5a-5b-5c-5d-5e-waste_diverted_to_disposal",
            29: "gri-environment-waste-306-5e-contextual_info",
            30: "gri-environment-waste-306-4b-4c-4d-waste_diverted_from_disposal",
            31: "gri-environment-waste-306-4e-contextual_info",
            32: "gri-environment-water-303-1b-1c-1d-interaction_with_water",
            33: "gri-environment-water-303-2a-profile_receiving_waterbody",
            34: "gri-environment-water-303-2a-management_water_discharge",
        }

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def get_energy_analyse(self):
        data = forward_request_with_jwt(
            view_class=EnergyAnalyzeView,
            original_request=self.request,
            url="/sustainapp/get_energy_analysis/",
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

    def get_waste_analyse(self):
        data = forward_request_with_jwt(
            view_class=GetWasteAnalysis,
            original_request=self.request,
            url="/sustainapp/get_waste_analysis/",
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

    def get_water_analyse(self):
        data = forward_request_with_jwt(
            view_class=WaterAnalyse,
            original_request=self.request,
            url="/sustainapp/get_water_analysis/",
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

    def get_301_analyse(self):
        data = forward_request_with_jwt(
            view_class=GetMaterialAnalysis,
            original_request=self.request,
            url="/sustainapp/get_material_analysis",
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

    def get_301_3a_3b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[6]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_2a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[5]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_1a_renewable_materials(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[4]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_1a_non_renewable_materials(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[3]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_123_collect(self):
        slugs = [self.slugs[0], self.slugs[1], self.slugs[2]]
        emission_analysis_objects = get_emission_analysis_as_per_report(
            report=self.report
        )
        slugs_dict = {
            "Scope-1": "gri-environment-emissions-301-a-scope-1",
            "Scope-2": "gri-environment-emissions-301-a-scope-2",
            "Scope-3": "gri-environment-emissions-301-a-scope-3",
        }
        slug_data = defaultdict(list)
        for emission_analyse_object in emission_analysis_objects:
            slug_data[slugs_dict[emission_analyse_object.scope]].append(
                {
                    "category": emission_analyse_object.category,
                    "subcategory": emission_analyse_object.subcategory,
                    "activity": emission_analyse_object.activity,
                    "activity_value": format_decimal_places(
                        emission_analyse_object.consumption
                    ),
                    "activity_unit": emission_analyse_object.unit,
                }
            )
        return slug_data

    def get_301_123_analyse(self):
        locations = set_locations_data(
            organisation=self.report.organization,
            corporate=self.report.corporate,
            location=None,
        )
        top_emission_by_scope, top_emission_by_source, top_emission_by_location = (
            get_top_emission_by_scope(
                locations=locations,
                user=self.report.user,
                start=self.report.start_date,
                end=self.report.end_date,
                path_slug={
                    "gri-environment-emissions-301-a-scope-1": "Scope 1",
                    "gri-environment-emissions-301-a-scope-2": "Scope 2",
                    "gri-environment-emissions-301-a-scope-3": "Scope 3",
                },
            )
        )

        # * Prepare response data
        response_data = dict()
        response_data["all_emission_by_scope"] = calculate_scope_contribution(
            key_name="scope", scope_total_values=top_emission_by_scope
        )
        response_data["all_emission_by_source"] = calculate_scope_contribution(
            key_name="source", scope_total_values=top_emission_by_source
        )
        response_data["all_emission_by_location"] = calculate_scope_contribution(
            key_name="location", scope_total_values=top_emission_by_location
        )
        response_data["top_5_emisson_by_source"] = response_data[
            "all_emission_by_source"
        ][0:5]
        response_data["top_5_emisson_by_location"] = response_data[
            "all_emission_by_location"
        ][0:5]
        return response_data

    def get_305_4abc(self):
        # TODO: Need more clarification from Sakthivel
        return None

    def get_305_5abc(self):
        # TODO: Need more clarification from Sakthivel
        return None

    def get_3_3cde(self):
        # TODO: Materiality Assessment Screen is pending
        return None

    def get_api_response(self):
        response_data = {}
        try:
            screen_twelve: ScreenTwelve = self.report.screen_twelve
            serializer = ScreenTwelveSerializer(screen_twelve)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenTwelve._meta.fields
                    if field.name not in ["id", "report"]
                }
            )

        self.set_raw_responses()
        self.set_data_points()
        response_data["3_3cde"] = self.get_3_3cde()
        response_data["305_123_collect"] = self.get_301_123_collect()
        response_data["305_123_analyse"] = self.get_301_123_analyse()
        response_data["305_4abc"] = self.get_305_4abc()
        response_data["305_5abc"] = self.get_305_5abc()
        response_data["301_1a_non_renewable_materials"] = (
            self.get_301_1a_non_renewable_materials()  # TODO: Make data from analyze
        )
        response_data["301_1a_renewable_materials"] = (
            self.get_301_1a_renewable_materials()  # TODO: Make data from analyze
        )
        response_data["301_2a"] = self.get_301_2a()
        response_data["301_3a_3b"] = self.get_301_3a_3b()
        response_data.update(
            {
                "306_5e": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[29]
                ),
                "306_5a_5b_5c_5d_5e": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[28]
                ),
                "306_2": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[27]
                ),
                "306_3b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[26]
                ),
                "306_3a_3b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[25]
                ),
                "306_1ab": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[24]
                ),
                "302_5c": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[23]
                ),
                "302_5b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[22]
                ),
                "302_5a_5b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[21]
                ),
                "302_4d": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[20]
                ),
                "302_4c": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[19]
                ),
                "302_4a_4b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[18]
                ),
                "302_3a_3b_3c_3d": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[17]
                ),
                "302_2c": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[16]
                ),
                "302_2b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[15]
                ),
                "302_2a": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[14]
                ),
                "302_1g": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[13]
                ),
                "302_1f": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[12]
                ),
                "302_1d": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[11]
                ),
                "302_1": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[10]
                ),
                "302_1c_1e": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[9]
                ),
                "302_1a_1b": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[8]
                ),
                "303_3a_3b_3c_3d": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[7]
                ),
                "306_4b_4c": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[30]
                ),
                "306_4e": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[31]
                ),
                "306_3": None,  # TODO: Add logic over here when clarified in figma.
                "303-1b-1c-1d": get_data_by_raw_response_and_index(
                    data_points=self.data_points, slug=self.slugs[32]
                ),
                "material_analyse": self.get_301_analyse(),
                "water_analyse": self.get_water_analyse(),
                "energy_analyse": self.get_energy_analyse(),
                "waste_analyse": self.get_waste_analyse(),
                "303-2a-profile_receiving_waterbody": collect_data_and_differentiate_by_location(
                    data_points=self.data_points.filter(path__slug=self.slugs[33])
                ),
                "303-2a-management_water_discharge": collect_data_and_differentiate_by_location(
                    data_points=self.data_points.filter(path__slug=self.slugs[34])
                ),
            }
        )
        return response_data

    def get_report_response(self):
        response_data = self.get_api_response()
        # * Convert keys from "-" into "_"
        response_data = {
            key.replace("-", "_"): value for key, value in response_data.items()
        }
        return response_data
