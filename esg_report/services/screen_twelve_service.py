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
    get_management_materiality_topics,
    calling_analyse_view_with_params,
)
from datametric.utils.analyse import set_locations_data
from sustainapp.Utilities.emission_analyse import (
    get_top_emission_by_scope,
    calculate_scope_contribution,
    disclosure_analyze_305_5,
    ghg_emission_intensity,
)
from sustainapp.Views.MaterialAnalyse import GetMaterialAnalysis
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
            35: "gri_collect_emission_management_material_topic",  # 12.1.1
            36: "gri_collect_water_and_effluents_management_material_topic",  # 12.3.1
            37: "gri_collect_energy_management_material_topic",  # 12.4.1
            38: "gri_collect_waste_management_material_topic",  # 12.5.1
            39: "gri-environment-water-303-4d-substances_of_concern",
            40: "gri-environment-water-303-3d-4e-sma",
            41: "gri-environment-emissions-GHG-emission-reduction-initiatives",
            42: "gri-environment-emissions-GHG emission-intensity",
            43: "gri-environment-air-quality-standard_methodologies",  # alag karo
            44: "gri-environment-air-quality-ods_production-standard-methodologies",  # alag karo
            45: "gri-environment-emissions-base_year",
            46: "gri-environment-emissions-consolidation_approach_q1",
            47: "gri-environment-emissions-consolidation_approach_q2",
            48: "gri-environment-emissions-standards_methodologies",
            49: "gri-environment-air-quality-management_of_material_topic",
            50: "gri_collect_materials_management_material_topic",
            51: "gri-environment-packaging-material-management-of-material-topic",
            # TODO : 12.2.1
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
        data = calling_analyse_view_with_params(
            view_url="get_water_analysis_api",
            report=self.report,
            request=self.request,
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
                    "emission": format_decimal_places(
                        emission_analyse_object.co2e_total / 1000
                    ),
                    "emission_unit": "tCO2e",
                }
            )
        return slug_data

    def get_301_123_analyse(self):
        locations = set_locations_data(
            organisation=self.report.organization,
            corporate=self.report.corporate,
            location=None,
        )
        (
            top_emission_by_scope,
            top_emission_by_source,
            top_emission_by_location,
            gases_data,
        ) = get_top_emission_by_scope(
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
        response_data["disclosure_analyze_305_5"] = disclosure_analyze_305_5(
            self.data_points.filter(path__slug=self.slugs[41])
        )
        response_data["ghg_emission_intensity"] = ghg_emission_intensity(
            self.data_points.filter(path__slug=self.slugs[42]),
            top_emission_by_scope,
            gases_data,
        )
        return response_data

    def get_emission_collect(self):
        base_year_data_points = self.data_points.filter(
            path__slug=self.slugs[45]
        ).order_by("index")
        emission_intensity_data_points = self.data_points.filter(
            path__slug=self.slugs[42]
        ).order_by("index")
        emission_reduction_data_points = self.data_points.filter(
            path__slug=self.slugs[41]
        ).order_by("index")
        consolidation_approach_for_emission_data_points = self.data_points.filter(
            path__slug=self.slugs[46]
        ).order_by("index")
        consolidation_assumption_considered_data_points = self.data_points.filter(
            path__slug=self.slugs[47]
        ).order_by("index")
        standard_methodology_used_data_points = self.data_points.filter(
            path__slug=self.slugs[48]
        ).order_by("index")
        data = {}
        data["base_year"] = collect_data_by_raw_response_and_index(
            data_points=base_year_data_points
        )
        data["emission_intensity"] = collect_data_by_raw_response_and_index(
            data_points=emission_intensity_data_points
        )
        data["emission_reduction"] = collect_data_by_raw_response_and_index(
            data_points=emission_reduction_data_points
        )
        data["consolidation_approach_for_emission"] = (
            collect_data_by_raw_response_and_index(
                data_points=consolidation_approach_for_emission_data_points
            )
        )
        data["consolidation_assumption_considered"] = (
            collect_data_by_raw_response_and_index(
                data_points=consolidation_assumption_considered_data_points
            )
        )
        data["standard_methodology_used"] = collect_data_by_raw_response_and_index(
            data_points=standard_methodology_used_data_points
        )
        return data

    def air_quality_collect(self):
        air_quality_standard_methodology_data_points = self.data_points.filter(
            path__slug=self.slugs[43]
        ).order_by("index")
        ods_standard_methodology_data_points = self.data_points.filter(
            path__slug=self.slugs[44]
        ).order_by("index")
        data = {}
        data["air_quality_standard_methodology"] = (
            collect_data_by_raw_response_and_index(
                data_points=air_quality_standard_methodology_data_points
            )
        )
        data["ods_standard_methodology"] = collect_data_by_raw_response_and_index(
            data_points=ods_standard_methodology_data_points
        )
        return data

    def get_air_quality_analyze(self):
        data = calling_analyse_view_with_params(
            view_url="air_quality_analyze",
            report=self.report,
            request=self.request,
        )
        return data

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
        response_data["emission_collect"] = self.get_emission_collect()
        response_data["air_quality_collect"] = self.air_quality_collect()
        response_data["air_quality_analyze"] = self.get_air_quality_analyze()
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
        response_data["3-3cde_12-1-1"] = get_management_materiality_topics(
            self.report, self.slugs[35]
        )
        response_data["3-3cde_12-2-1_materials"] = get_management_materiality_topics(
            self.report, self.slugs[50]
        )
        response_data["3-3cde_12-2-1_packaging"] = get_management_materiality_topics(
            self.report, self.slugs[51]
        )
        response_data["3-3cde_12-3-1"] = get_management_materiality_topics(
            self.report, self.slugs[36]
        )
        response_data["3-3cde_12-4-1"] = get_management_materiality_topics(
            self.report, self.slugs[37]
        )
        response_data["3-3cde_12-5-1"] = get_management_materiality_topics(
            self.report, self.slugs[38]
        )
        response_data["3-3cde_12-7-1"] = get_management_materiality_topics(
            self.report, self.slugs[49]
        )
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
                "303_4d_substances_of_concern": collect_data_by_raw_response_and_index(
                    data_points=self.data_points.filter(path__slug=self.slugs[39])
                ),
                "303_3d_4e_sma": collect_data_and_differentiate_by_location(
                    data_points=self.data_points.filter(path__slug=self.slugs[40])
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
