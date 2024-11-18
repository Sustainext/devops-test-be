from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_data_by_raw_response_and_index,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    get_data_by_raw_response_and_index,
    forward_request_with_jwt,
    calling_analyse_view_with_params,
    calling_analyse_view_with_params_for_same_year,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APIRequestFactory
from sustainapp.Views.Analyse.Social.EmploymentAnalyze import EmploymentAnalyzeView
from sustainapp.Views.Analyse.Social.TrainingAnalyse import TrainingSocial
from sustainapp.Views.Analyse.Social.IllnessAnalyse import IllnessAnalysisView
from esg_report.Serializer.ScreenThirteenSerializer import ScreenThirteenSerializer
from sustainapp.models import Report
from esg_report.models.ScreenThirteen import ScreenThirteen


class ScreenThirteenService:
    def __init__(self, request, report_id):
        self.request = request
        self.report = Report.objects.get(id=report_id)
        self.slugs = {
            0: "gri-general-workforce_employees-2-7-a-b-permanent_employee",
            1: "gri-general-workforce_employees-2-7-a-b-temporary_employee",
            3: "gri-general-workforce_employees-methodologies-2-7c",
            4: "gri-general-workforce_employees-data-2-7c",
            5: "gri-general-workforce_employees-contextual-2-7d",
            6: "gri-general-workforce_employees-fluctuations-2-7e",
            7: "gri-social-parental_leave-401-3a-3b-3c-3d-parental_leave",
            8: "gri-social-human_rights-409-1b-measures_taken",
            9: "gri-social-human_rights-409-1a-operations_forced_labor",
            10: "gri-social-human_rights-409-1a-suppliers_forced_labor",
            11: "gri-social-human_rights-408-1a-1b-operations_risk_child_labour",
            12: "gri-social-human_rights-408-1a-1b-operations_young_worker_exposed",
            13: "gri-social-human_rights-408-1a-1b-supplier_risk_child_labor",
            14: "gri-social-human_rights-408-1a-1b-supplier_young_worker_exposed",
            15: "gri-social-diversity_of_board-405-1a-number_of_individuals",
            16: "gri-social-diversity_of_board-405-1b-number_of_employee",
            17: "gri-social-salary_ratio-405-2a-number_of_individuals",
            18: "gri-social-salary_ratio-405-2a-ratio_of_remuneration",
            19: "gri-social-training_hours-404-1a-number_of_hours",
            20: "gri-social-human_rights-410-1a-security_personnel",
            21: "gri-social-ohs-403-1a-ohs_management_system",
            22: "gri-social-ohs-403-1b-scope_of_workers",
            23: "gri-social-ohs-403-3a-ohs_functions",
            24: "gri-social-ohs-403-4a-ohs_system_1",
            25: "gri-social-ohs-403-4a-ohs_system_2",
            26: "gri-social-ohs-403-4d-formal_joint",
            27: "gri-social-ohs-403-6a-access_non_occupational",
            28: "gri-social-ohs-403-6a-scope_of_access",
            29: "gri-social-ohs-403-6a-voluntary_health",
            30: "gri-social-ohs-403-6a-health_risk",
            31: "gri-social-ohs-403-6b-workers_access",
            32: "gri-social-ohs-403-7a-negative_occupational",
            33: "gri-social-ohs-403-7a-hazards_risks",
            34: "gri-social-ohs-403-2a-process_for_hazard",
            35: "gri-social-ohs-403-2b-quality_assurance",
            36: "gri-social-ohs-403-2c-worker_right",
            37: "gri-social-ohs-403-2d-work_related_incident",
            38: "gri-social-ohs-403-9a-number_of_injuries_emp",
            39: "gri-social-ohs-403-9b-number_of_injuries_workers",
            40: "gri-social-ohs-403-9c-9d-work_related_hazards",
            41: "gri-social-ohs-403-9e-number_of_hours",
            42: "gri-social-ohs-403-9f-workers_excluded",
            43: "gri-social-ohs-403-9g-sma",
            44: "gri-social-ohs-403-10c-work_related_hazards",
            45: "gri-social-ohs-403-10d-workers_excluded",
            46: "gri-social-ohs-403-10e-sma",
            47: "gri-social-ohs-403-5a-ohs_training",
            48: "gri-social-ohs-403-8b-workers_excluded",
            49: "gri-social-ohs-403-8c-sma",
            50: "gri-social-notice_period-402-1a-collective_bargaining",
            51: "gri-social-collective_bargaining-407-1a-operations",
            52: "gri-social-collective_bargaining-407-1a-suppliers",
            53: "gri-social-incidents_of_discrimination-406-1a-incidents_of_discrimination",
            54: "gri-social-incidents_of_discrimination-406-1b-status",
            55: "gri-social-collective_bargaining-407-1b-measures",
            56: "gri-social-indigenous_people-411-1a-incidents",
            57: "gri-social-indigenous_people-411-1b-status",
            58: "gri-social-human_rights-408-1c-measures_taken",
            59: "gri-social-employee_hires-401-1a-new_emp_hire-permanent_emp",
            60: "gri-social-employee_hires-401-1a-new_emp_hire-temp_emp",
            61: "gri-social-employee_hires-401-1a-new_emp_hire-nonguaranteed",
            62: "gri-social-employee_hires-401-1a-new_emp_hire-fulltime",
            63: "gri-social-employee_hires-401-1a-new_emp_hire-parttime",
            64: "gri-social-employee_hires-401-1a-emp_turnover-permanent_emp",
            65: "gri-social-employee_hires-401-1a-emp_turnover-temp_emp",
            66: "gri-social-employee_hires-401-1a-emp_turnover-nonguaranteed",
            67: "gri-social-employee_hires-401-1a-emp_turnover-fulltime",
            68: "gri-social-employee_hires-401-1a-emp_turnover-parttime",
            69: "gri-social-benefits-401-2a-benefits_provided",
            70: "gri-social-benefits-401-2b-significant_loc",
            71: "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1b-s2",
            72: "gri-economic-ratios_of_standard_entry-202-1c-location",
            73: "gri-economic-ratios_of_standard_entry-202-1d-definition",
            74: "gri-social-human_rights-410-1b-training_requirements",
            75: "gri-social-skill_upgrade-403-9c-9d-programs",
            76: "gri-social-salary_ratio-405-2b-significant_locations",
            77: "gri-general-collective_bargaining-2-30-a-percentage",
            78: "gri-general-collective_bargaining-2-30-b-employees",
            79: "gri-general-workforce_other_workers-workers-2-8-a",
            80: "gri-general-workforce_other_workers-methodologies-2-8b",
            81: "gri-general-workforce_other_workers-fluctuations-2-8c",
            82: "gri-social-ohs-403-8a-number_of_employees",
            83: "gri-social-notice_period-402-1a-minimum",  #
            84: "gri-social-notice_period-402-1a-collective_bargaining",
        }

    def get_403_2a_process_for_hazard(self):
        local_raw_responses = self.raw_responses.filter(path__slug=self.slugs[34])

    def get_401_ab_social(self):
        data = forward_request_with_jwt(
            view_class=EmploymentAnalyzeView,
            original_request=self.request,
            url="/sustainapp/get_employment_analysis",
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

    def get_403_2a(self):
        local_raw_responses = self.raw_responses.filter(
            path__slug=self.slugs[34]
        ).first()
        if local_raw_responses is not None:
            return local_raw_responses.data[0]

    def get_403(self):
        data = forward_request_with_jwt(
            view_class=IllnessAnalysisView,
            original_request=self.request,
            url="/sustainapp/get_ohs_analysis/",
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

    def get_404_social(self):
        data = forward_request_with_jwt(
            view_class=TrainingSocial,
            original_request=self.request,
            url="/sustainapp/get_training_social_analysis/",
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

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_202_1c(self):
        slug = self.slugs[72]
        local_raw_responses = self.raw_responses.filter(path__slug=slug).first()
        if local_raw_responses is not None:
            return [local_raw_responses.data[0]]

    def get_api_response(self):
        response_data = {}
        try:
            screen_thirteen = ScreenThirteen.objects.get(report=self.report)
            serializer = ScreenThirteenSerializer(screen_thirteen)
            response_data.update(serializer.data)
        except ScreenThirteen.DoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenThirteen._meta.fields
                    if field.name not in ["id", "report"]
                }
            )
        self.set_data_points()
        self.set_raw_responses()
        response_data["2_7_a_b_permanent_employee"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[0])
            )
        )
        response_data["2_7_a_b_temporary_employee"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[1])
            )
        )
        response_data["2_7_c_methodologies"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[3])
        )
        response_data["2_7_c_data"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[4])
        )
        response_data["2_7_d_contextual"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[5])
        )
        response_data["2_7_e_fluctuations"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[6])
        )
        response_data["401_social_analyse"] = self.get_401_ab_social()
        response_data["401_3a_3b_3c_3d_parental_leave"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[7])
            )
        )
        response_data["404_social_analyse"] = self.get_404_social()
        response_data["409-1b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[8])
        )
        response_data["409-1a_operations_forced_labor"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[9])
            )
        )
        response_data["409-1a_suppliers_forced_labor"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[10])
            )
        )
        response_data["408-1a-1b-operations_risk_child_labour"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[11])
            )
        )
        response_data["408-1a-1b-operations_young_worker_exposed"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[12])
            )
        )
        response_data["408-1a-1b-supplier_risk_child_labor"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[13])
            )
        )
        response_data["408-1a-1b-supplier_young_worker_exposed"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[14])
            )
        )
        response_data["405-1a-number_of_individuals"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[15])
            )
        )
        response_data["405-1b-number_of_individuals"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[16])
            )
        )
        response_data[
            "405-2a-number_of_individuals"
        ] = (  # TODO: Data Point is not coming properly
            self.raw_responses.filter(path__slug=self.slugs[17]).first().data
            if self.raw_responses.filter(path__slug=self.slugs[17]).exists()
            else None
        )
        response_data["405-2a-ratio_of_remuneration"] = (
            self.raw_responses.filter(path__slug=self.slugs[18]).first().data
            if self.raw_responses.filter(path__slug=self.slugs[18]).exists()
            else None
        )
        response_data["404-1a-number_of_hours"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[19])
            )
        )
        response_data["410-1a-security_personnel"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[20])
            )
        )
        response_data["403-1a-ohs_management_system"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[21])
            )
        )
        response_data["403-1b-scope_of_workers"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[22])
            )
        )

        response_data["403-3a-ohs_functions"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[23])
            )
        )
        response_data["403-4a-ohs_system_1"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[24])
            )
        )
        response_data["403-4a-ohs_system_2"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[25])
            )
        )
        response_data["403-4b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[26])
        )

        response_data["403-6a-access_non_occupational"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[27])
            )
        )
        response_data["403-6a-scope_of_access"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[28])
            )
        )
        response_data["403-6a-voluntary_health"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[29])
            )
        )
        response_data["403-6a-health_risk"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[30])
            )
        )

        response_data["403-6b-workers_access"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[31])
            )
        )
        response_data["403-7a-negative_occupational"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[32])
            )
        )
        response_data["403-7a-hazards_risks"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[33])
            )
        )
        response_data["403-2a-process_for_hazard"] = (
            self.get_403_2a()
        )  # TODO: Redo it with data points after data metrics get fixed.
        response_data["403-2b-quality_assurance"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[35])
            )
        )
        response_data["403-2c-worker_right"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[36])
            )
        )
        response_data["403-2d"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[37])
        )

        response_data["get_403_analyse"] = self.get_403()
        response_data["403_9a"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[38])
        )
        response_data["403_9b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[39])
        )
        response_data["403_9c_9d"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[40])
        )
        response_data["403_9e"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[41])
        )
        response_data["403_9f"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[42])
        )
        response_data["403_9g"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[43])
        )
        response_data["403-10c"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[43])
        )
        response_data["403-10d"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[45])
        )
        response_data["403-10e"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[46])
        )
        response_data["403-5a"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[47])
        )
        response_data["403-8b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[48])
        )
        response_data["403-8c"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[49])
        )
        response_data["402-1a_collective_bargainging_agreements"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[50])
            )
        )
        response_data["407-1a-operations"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[51])
        )
        response_data["407-1a-suppliers"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[52])
        )
        response_data["2_30_a"] = calling_analyse_view_with_params(
            view_url="get_general_collective_bargaining_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["407_1_analyse"] = calling_analyse_view_with_params(
            view_url="get_collective_bargaining_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["406_1_analyse"] = calling_analyse_view_with_params(
            view_url="get_non_discrimination_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["408_1a_1b_analyse"] = calling_analyse_view_with_params(
            view_url="get_child_labor_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["406_1a"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[53])
        )
        response_data["406_1b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[54])
        )
        response_data["407_1b"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[55])
        )
        response_data["411_1a"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[56])
        )
        response_data["411_1b"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[57])
        )
        response_data["408-1c-measures_taken"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[58])
            )
        )
        response_data["401-1a"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[59])
        )
        response_data["401-1a-new_emp_hire-temp_emp"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[60])
            )
        )
        response_data["401-1a-new_emp_hire-nonguaranteed"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[61])
            )
        )
        response_data["401-1a-new_emp_hire-fulltime"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[62])
            )
        )
        response_data["401-1a-new_emp_hire-parttime"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[63])
            )
        )
        response_data["401-1a-emp_turnover-permanent_emp"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[64])
            )
        )
        response_data["401-1a-emp_turnover-temp_emp"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[65])
            )
        )
        response_data["401-1a-emp_turnover-nonguaranteed"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[66])
            )
        )
        response_data["401-1a-emp_turnover-fulltime"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[67])
            )
        )
        response_data["401-1a-emp_turnover-parttime"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[68])
            )
        )
        response_data["401-2a-benefits_provided"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[69])
            )
        )
        response_data["401-2b-significant_loc"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[70])
            )
        )
        response_data["202_1b"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[71])
        )
        response_data["202_1c"] = self.get_202_1c()
        response_data["202_1d"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[73])
        )
        response_data["202_1a_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_economic_market_presence",
                report=self.report,
                request=self.request,
            )
        )
        response_data["408_1a_408_1b_analyse"] = calling_analyse_view_with_params(
            view_url="get_child_labor_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["405_1a_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_diversity_inclusion_analysis",
                report=self.report,
                request=self.request,
            )
        )
        response_data["410-1b-training_requirements"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[74])
            )
        )
        response_data["404_1a_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_training_social_analysis",
                report=self.report,
                request=self.request,
            )
        )
        response_data["404_2a_2b_collect"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[75])
        )
        response_data["405-2b-significant_locations"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[76])
            )
        )
        response_data["405-2a_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_diversity_inclusion_analysis",
                report=self.report,
                request=self.request,
            )
        )
        response_data["2_30_a"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[77])
        )
        response_data["2_30_b"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[78])
        )
        response_data["2_30_a_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_general_collective_bargaining_analysis",
                report=self.report,
                request=self.request,
            )
        )
        response_data["2_7a_2_7b_analyse"] = (
            calling_analyse_view_with_params_for_same_year(
                view_url="get_general_employee_analysis",
                report=self.report,
                request=self.request,
            )
        )
        response_data["409_1a_analyse"] = calling_analyse_view_with_params(
            view_url="get_forced_labor_analysis",
            report=self.report,
            request=self.request,
        )
        response_data["2_8_a"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[79])
        )
        response_data["2_8_b"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[80])
        )
        response_data["2_8_c"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[81])
        )
        response_data["403-8a"] = collect_data_and_differentiate_by_location(
            data_points=self.data_points.filter(path__slug=self.slugs[82])
        )
        response_data["402_1a_minimum_number_of_weeks"] = (
            collect_data_and_differentiate_by_location(
                data_points=self.data_points.filter(path__slug=self.slugs[83])
            )
        )
        return response_data

    def get_report_response(self):
        response_data = self.get_api_response()
        # * Convert keys of response_data from "-" to "_"
        response_data = {
            key.replace("-", "_"): value for key, value in response_data.items()
        }
        return response_data
