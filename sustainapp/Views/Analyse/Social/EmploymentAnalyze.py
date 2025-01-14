from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from django.db.models import Sum
from datametric.utils.analyse import filter_by_start_end_dates, get_raw_response_filters
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from math import floor
from datametric.utils.analyse import safe_divide_percentage
import logging

logger = logging.getLogger("django")


def get_integer(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to an integer")
    else:
        raise TypeError(f"Expected int or str, got {type(value).__name__}")


def get_value(object_value):
    if object_value is None:
        return 0
    else:
        return object_value


def get_object_value(object_value):
    if object_value is None:
        return 0
    else:
        return object_value.value


def get_integer(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to an integer")
    else:
        raise TypeError(f"Expected int or str, got {type(value).__name__}")


class EmploymentAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    new_employee_hire_path_slugs = [
        "gri-social-employee_hires-401-1a-new_emp_hire-permanent_emp",
        "gri-social-employee_hires-401-1a-new_emp_hire-temp_emp",
        "gri-social-employee_hires-401-1a-new_emp_hire-nonguaranteed",
        "gri-social-employee_hires-401-1a-new_emp_hire-fulltime",
        "gri-social-employee_hires-401-1a-new_emp_hire-parttime",
    ]
    employee_turnover_path_slugs = [
        "gri-social-employee_hires-401-1a-emp_turnover-permanent_emp",
        "gri-social-employee_hires-401-1a-emp_turnover-temp_emp",
        "gri-social-employee_hires-401-1a-emp_turnover-nonguaranteed",
        "gri-social-employee_hires-401-1a-emp_turnover-fulltime",
        "gri-social-employee_hires-401-1a-emp_turnover-parttime",
    ]
    employee_benefits_path_slugs = [
        "gri-social-benefits-401-2a-benefits_provided",
        "gri-social-benefits-401-2a-benefits_provided_tab_1",
        "gri-social-benefits-401-2a-benefits_provided_tab_2",
        "gri-social-benefits-401-2a-benefits_provided_tab_3",
    ]
    employee_parental_leave_path_slugs = [
        "gri-social-parental_leave-401-3a-3b-3c-3d-parental_leave"
    ]

    new_employee_paths = {
        "permanent": new_employee_hire_path_slugs[0],
        "temporary": new_employee_hire_path_slugs[1],
        "nonguaranteed": new_employee_hire_path_slugs[2],
        "fulltime": new_employee_hire_path_slugs[3],
        "parttime": new_employee_hire_path_slugs[4],
    }
    employee_turnover_paths = {
        "permanent": employee_turnover_path_slugs[0],
        "temporary": employee_turnover_path_slugs[1],
        "nonguaranteed": employee_turnover_path_slugs[2],
        "fulltime": employee_turnover_path_slugs[3],
        "parttime": employee_turnover_path_slugs[4],
    }
    metric_names_new_employee = {
        "30": "yearsold30",
        "30-50": "yearsold30-50",
        "50": "yearsold50",
        "total": "total",
    }
    metric_names_employeeTurnover = {
        "30": "yearsold30",
        "30-50": "yearsold30-50",
        "50": "yearsold50",
        "end": "end",
        "beginning": "beginning",
    }

    def get_employment_turnover(self, employment_turnover_data_points):
        def get_average(data_points):
            # * Check if data points are there in January and if yes, then calculate the average of beginning and end
            jan_data_points = data_points.filter(month=1)
            jan_data = collect_data_by_raw_response_and_index(
                data_points=jan_data_points
            )
            total_beginning = sum(point.get("beginning", 0) for point in jan_data)
            total_end = sum(point.get("end", 0) for point in jan_data)
            return floor((total_beginning + total_end) / 2)

        employee_turnover_paths = {
            "Permanent employee": self.employee_turnover_path_slugs[0],
            "Temporary employee": self.employee_turnover_path_slugs[1],
            "Non Guaranteed employee": self.employee_turnover_path_slugs[2],
            "Full time employee": self.employee_turnover_path_slugs[3],
            "Part time employee": self.employee_turnover_path_slugs[4],
        }
        local_response_data = []
        for key in employee_turnover_paths:
            local_response_dict = {}
            employee_turnover_key_jan_data_points = (
                employment_turnover_data_points.filter(
                    path__slug=employee_turnover_paths[key], month=1
                )
            )
            employee_turnover_key_data_points = employment_turnover_data_points.filter(
                path__slug=employee_turnover_paths[key]
            )
            key_average = get_average(employee_turnover_key_jan_data_points)
            percentage_of_male_employee = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key], index=0
                            ).exclude(data_metric__name__in=["end", "beginning"])
                        )
                    ]
                ),
                key_average,
            )
            percentage_of_female_employee = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key], index=1
                            ).exclude(data_metric__name__in=["end", "beginning"])
                        )
                    ]
                ),
                key_average,
            )
            percentage_of_non_binary_employee = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key], index=2
                            ).exclude(data_metric__name__in=["end", "beginning"])
                        )
                    ]
                ),
                key_average,
            )
            yearsold30 = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key]
                            ).filter(data_metric__name="yearsold30")
                        )
                    ]
                ),
                key_average,
            )
            yearsold50 = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key]
                            ).filter(data_metric__name="yearsold50")
                        )
                    ]
                ),
                key_average,
            )
            yearsold30to50 = safe_divide_percentage(
                sum(
                    [
                        sum(d.values())
                        for d in collect_data_by_raw_response_and_index(
                            employee_turnover_key_data_points.filter(
                                path__slug=employee_turnover_paths[key]
                            ).filter(data_metric__name="yearsold30to50")
                        )
                    ]
                ),
                key_average,
            )
            local_response_dict = {
                "type_of_employee": key,
                "percentage_of_male_employee": percentage_of_male_employee,
                "percentage_of_female_employee": percentage_of_female_employee,
                "percentage_of_non_binary_employee": percentage_of_non_binary_employee,
                "yearsold30": yearsold30,
                "yearsold50": yearsold50,
                "yearsold30to50": yearsold30to50,
                "total": key_average,
            }
            local_response_data.append(local_response_dict)
        local_response_data.append(
            {
                "type_of_employee": "Total",
                "total": sum(
                    [
                        d["total"]
                        for d in local_response_data
                        if d["type_of_employee"] != "Total"
                    ]
                ),
            }
        )
        return local_response_data

    def get_response_dictionaries(self):
        new_employee_reponse_table = {
            # permanent
            "new_employee_permanent_male_percent": 0,
            "new_employee_permanent_female_percent": 0,
            "new_employee_permanent_non_binary_percent": 0,
            "new_employee_permanent_30_percent": 0,
            "new_employee_permanent_30-50_percent": 0,
            "new_employee_permanent_50_percent": 0,
            # temporary
            "new_employee_temporary_male_percent": 0,
            "new_employee_temporary_female_percent": 0,
            "new_employee_temporary_non_binary_percent": 0,
            "new_employee_temporary_30_percent": 0,
            "new_employee_temporary_30-50_percent": 0,
            "new_employee_temporary_50_percent": 0,
            # non guaranteed
            "new_employee_non_guaranteed_male_percent": 0,
            "new_employee_non_guaranteed_female_percent": 0,
            "new_employee_non_guaranteed_non_binary_percent": 0,
            "new_employee_non_guaranteed_30_percent": 0,
            "new_employee_non_guaranteed_30-50_percent": 0,
            "new_employee_non_guaranteed_50_percent": 0,
            # full time
            "new_employee_full_time_male_percent": 0,
            "new_employee_full_time_female_percent": 0,
            "new_employee_full_time_non_binary_percent": 0,
            "new_employee_full_time_30_percent": 0,
            "new_employee_full_time_30-50_percent": 0,
            "new_employee_full_time_50_percent": 0,
            # part time
            "new_employee_part_time_male_percent": 0,
            "new_employee_part_time_female_percent": 0,
            "new_employee_part_time_non_binary_percent": 0,
            "new_employee_part_time_30_percent": 0,
            "new_employee_part_time_30-50_percent": 0,
            "new_employee_part_time_50_percent": 0,
        }
        employee_turnover_reponse_table = {
            # permanent
            "employee_turnover_permanent_male_percent": 0,
            "employee_turnover_permanent_female_percent": 0,
            "employee_turnover_permanent_non_binary_percent": 0,
            "employee_turnover_permanent_30_percent": 0,
            "employee_turnover_permanent_30-50_percent": 0,
            "employee_turnover_permanent_50_percent": 0,
            # temporary_turnover
            "employee_turnover_temporary_male_percent": 0,
            "employee_turnover_temporary_female_percent": 0,
            "employee_turnover_temporary_non_binary_percent": 0,
            "employee_turnover_temporary_30_percent": 0,
            "employee_turnover_temporary_30-50_percent": 0,
            "employee_turnover_temporary_50_percent": 0,
            # guaranteed_turnover
            "employee_turnover_non_guaranteed_male_percent": 0,
            "employee_turnover_non_guaranteed_female_percent": 0,
            "employee_turnover_non_guaranteed_non_binary_percent": 0,
            "employee_turnover_non_guaranteed_30_percent": 0,
            "employee_turnover_non_guaranteed_30-50_percent": 0,
            "employee_turnover_non_guaranteed_50_percent": 0,
            # fulltime_turnover
            "employee_turnover_full_time_male_percent": 0,
            "employee_turnover_full_time_female_percent": 0,
            "employee_turnover_full_time_non_binary_percent": 0,
            "employee_turnover_full_time_30_percent": 0,
            "employee_turnover_full_time_30-50_percent": 0,
            "employee_turnover_full_time_50_percent": 0,
            # parttime_turnover
            "employee_turnover_part_time_male_percent": 0,
            "employee_turnover_part_time_female_percent": 0,
            "employee_turnover_part_time_non_binary_percent": 0,
            "employee_turnover_part_time_30_percent": 0,
            "employee_turnover_part_time_30-50_percent": 0,
            "employee_turnover_part_time_50_percent": 0,
        }

        benefits_response_table = {
            # "fulltime, partime, temporary"
            "life_insurance_full_time": None,
            "life_insurance_part_time": None,
            "life_insurance_temporary": None,
            "healthcare_full_time": None,
            "healthcare_part_time": None,
            "healthcare_temporary": None,
            "disability_cover_full_time": None,
            "disability_cover_part_time": None,
            "disability_cover_temporary": None,
            "parental_leave_full_time": None,
            "parental_leave_part_time": None,
            "parental_leave_temporary": None,
            "retirement_full_time": None,
            "retirement_part_time": None,
            "retirement_temporary": None,
            "stock_ownership_full_time": None,
            "stock_ownership_part_time": None,
            "stock_ownership_temporary": None,
        }
        parental_leave_response_table = {
            # "fulltime, partime, temporary"
            "entitlement_male": 0,
            "entitlement_female": 0,
            "entitlement_total": 0,
            "taking_male": 0,
            "taking_female": 0,
            "taking_total": 0,
            "return_to_post_work_male": 0,
            "return_to_post_work_female": 0,
            "return_to_post_work_total": 0,
            "retained_12_mts_male": 0,
            "retained_12_mts_female": 0,
            "retained_12_mts_total": 0,
        }

        return (
            new_employee_reponse_table,
            employee_turnover_reponse_table,
            benefits_response_table,
            parental_leave_response_table,
        )

    def process_dataPoints(
        self,
        new_employ_dps,
        emp_turnover_dps,
        benefits_data_points,
        parental_leave_data_points,
    ):
        (
            new_employee_reponse_table,
            employee_turnover_reponse_table,
            benefits_response_table,
            parental_leave_response_table,
        ) = self.get_response_dictionaries()

        dp_employ_permanent = []
        dp_employ_permanent_qs = []

        dp_employ_full_time = []
        dp_employ_temporary = []
        dp_employ_non_guaranteed = []
        dp_employ_part_time = []
        dp_employ_permanent_qs = []

        for dp in new_employ_dps:
            if dp.path.slug == self.new_employee_paths["permanent"]:
                dp_employ_permanent.append(dp)
            if dp.path.slug == self.new_employee_paths["temporary"]:
                dp_employ_temporary.append(dp)
            if dp.path.slug == self.new_employee_paths["nonguaranteed"]:
                dp_employ_non_guaranteed.append(dp)
            if dp.path.slug == self.new_employee_paths["fulltime"]:
                dp_employ_full_time.append(dp)
            if dp.path.slug == self.new_employee_paths["parttime"]:
                dp_employ_part_time.append(dp)
            # male, female, non-binary ==> index; 30,30-50, 50 is metric_name

        # new_employee_permanent

        if dp_employ_permanent:
            dp_employ_permanent_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_permanent]
            )
        else:
            dp_employ_permanent_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model
        ne_male_permanent_qs = dp_employ_permanent_qs.filter(
            index=0, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_female_permanent_qs = dp_employ_permanent_qs.filter(
            index=1, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_nb_permanent_qs = dp_employ_permanent_qs.filter(
            index=2, metric_name="total"
        ).aggregate(Sum("number_holder"))

        ne_permanent_30_qs = dp_employ_permanent_qs.filter(
            metric_name="yearsold30"
        ).aggregate(Sum("number_holder"))
        ne_permanent_30_50_qs = dp_employ_permanent_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        ne_permanent_50_qs = dp_employ_permanent_qs.filter(
            metric_name="yearsold50"
        ).aggregate(Sum("number_holder"))

        total_permanent = (
            get_value(ne_male_permanent_qs["number_holder__sum"])
            + get_value(ne_female_permanent_qs["number_holder__sum"])
            + get_value(ne_nb_permanent_qs["number_holder__sum"])
        )

        ne_per_male_percent = safe_divide_percentage(
            get_value(ne_male_permanent_qs["number_holder__sum"]), total_permanent
        )
        ne_per_female_percent = safe_divide_percentage(
            get_value(ne_female_permanent_qs["number_holder__sum"]), total_permanent
        )
        ne_per_nb_percent = safe_divide_percentage(
            get_value(ne_nb_permanent_qs["number_holder__sum"]), total_permanent
        )
        ne_permanent_30_pc = safe_divide_percentage(
            get_value(ne_permanent_30_qs["number_holder__sum"]), total_permanent
        )
        ne_permanent_30_50_pc = safe_divide_percentage(
            get_value(ne_permanent_30_50_qs["number_holder__sum"]), total_permanent
        )
        ne_permanent_50_pc = safe_divide_percentage(
            get_value(ne_permanent_50_qs["number_holder__sum"]), total_permanent
        )

        new_employee_reponse_table["new_employee_permanent_male_percent"] = (
            ne_per_male_percent
        )
        new_employee_reponse_table["new_employee_permanent_female_percent"] = (
            ne_per_female_percent
        )
        new_employee_reponse_table["new_employee_permanent_non_binary_percent"] = (
            ne_per_nb_percent
        )
        new_employee_reponse_table["new_employee_permanent_30_percent"] = (
            ne_permanent_30_pc
        )
        new_employee_reponse_table["new_employee_permanent_30-50_percent"] = (
            ne_permanent_30_50_pc
        )
        new_employee_reponse_table["new_employee_permanent_50_percent"] = (
            ne_permanent_50_pc
        )
        new_employee_reponse_table["new_employee_permanent_total"] = total_permanent

        # new_employee temporary

        if dp_employ_temporary:
            dp_employ_temporary_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_temporary]
            )
        else:
            dp_employ_temporary_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        ne_male_temporary_qs = dp_employ_temporary_qs.filter(
            index=0, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_female_temporary_qs = dp_employ_temporary_qs.filter(
            index=1, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_nb_temporary_qs = dp_employ_temporary_qs.filter(
            index=2, metric_name="total"
        ).aggregate(Sum("number_holder"))

        ne_temporary_30_qs = dp_employ_temporary_qs.filter(
            metric_name="yearsold30"
        ).aggregate(Sum("number_holder"))
        ne_temporary_30_50_qs = dp_employ_temporary_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        ne_temporary_50_qs = dp_employ_temporary_qs.filter(
            metric_name="yearsold50"
        ).aggregate(Sum("number_holder"))

        total_temporary = (
            get_value(ne_male_temporary_qs["number_holder__sum"])
            + get_value(ne_female_temporary_qs["number_holder__sum"])
            + get_value(ne_nb_temporary_qs["number_holder__sum"])
        )

        ne_temp_male_percent = safe_divide_percentage(
            get_value(ne_male_temporary_qs["number_holder__sum"]), total_temporary
        )
        ne_temp_female_percent = safe_divide_percentage(
            get_value(ne_female_temporary_qs["number_holder__sum"]), total_temporary
        )
        ne_temp_nb_percent = safe_divide_percentage(
            get_value(ne_nb_temporary_qs["number_holder__sum"]), total_temporary
        )
        ne_temp_30_pc = safe_divide_percentage(
            get_value(ne_temporary_30_qs["number_holder__sum"]), total_temporary
        )
        ne_temp_30_50_pc = safe_divide_percentage(
            get_value(ne_temporary_30_50_qs["number_holder__sum"]), total_temporary
        )
        ne_temp_50_pc = safe_divide_percentage(
            get_value(ne_temporary_50_qs["number_holder__sum"]), total_temporary
        )

        new_employee_reponse_table["new_employee_temporary_male_percent"] = (
            ne_temp_male_percent
        )
        new_employee_reponse_table["new_employee_temporary_female_percent"] = (
            ne_temp_female_percent
        )
        new_employee_reponse_table["new_employee_temporary_non_binary_percent"] = (
            ne_temp_nb_percent
        )
        new_employee_reponse_table["new_employee_temporary_30_percent"] = ne_temp_30_pc
        new_employee_reponse_table["new_employee_temporary_30-50_percent"] = (
            ne_temp_30_50_pc
        )
        new_employee_reponse_table["new_employee_temporary_50_percent"] = ne_temp_50_pc
        new_employee_reponse_table["new_employee_temporary_total"] = total_temporary
        # new_employee non guaranteed

        if dp_employ_non_guaranteed:
            dp_employ_non_guaranteed_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_non_guaranteed]
            )
        else:
            dp_employ_non_guaranteed_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        ne_male_ng_qs = dp_employ_non_guaranteed_qs.filter(
            index=0, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_female_ng_qs = dp_employ_non_guaranteed_qs.filter(
            index=1, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_nb_ng_qs = dp_employ_non_guaranteed_qs.filter(
            index=2, metric_name="total"
        ).aggregate(Sum("number_holder"))

        ne_ng_30_qs = dp_employ_non_guaranteed_qs.filter(
            metric_name="yearsold30"
        ).aggregate(Sum("number_holder"))
        ne_ng_30_50_qs = dp_employ_non_guaranteed_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        ne_ng_50_qs = dp_employ_non_guaranteed_qs.filter(
            metric_name="yearsold50"
        ).aggregate(Sum("number_holder"))

        total_ng = (
            get_value(ne_male_ng_qs["number_holder__sum"])
            + get_value(ne_female_ng_qs["number_holder__sum"])
            + get_value(ne_nb_ng_qs["number_holder__sum"])
        )

        ne_ng_male_percent = safe_divide_percentage(
            get_value(ne_male_ng_qs["number_holder__sum"]), total_ng
        )
        ne_ng_female_percent = safe_divide_percentage(
            get_value(ne_female_ng_qs["number_holder__sum"]), total_ng
        )
        ne_ng_nb_percent = safe_divide_percentage(
            get_value(ne_nb_ng_qs["number_holder__sum"]), total_ng
        )
        ne_ng_30_pc = safe_divide_percentage(
            get_value(ne_ng_30_qs["number_holder__sum"]), total_ng
        )
        ne_ng_30_50_pc = safe_divide_percentage(
            get_value(ne_ng_30_50_qs["number_holder__sum"]), total_ng
        )
        ne_ng_50_pc = safe_divide_percentage(
            get_value(ne_ng_50_qs["number_holder__sum"]), total_ng
        )

        new_employee_reponse_table["new_employee_non_guaranteed_male_percent"] = (
            ne_ng_male_percent
        )
        new_employee_reponse_table["new_employee_non_guaranteed_female_percent"] = (
            ne_ng_female_percent
        )
        new_employee_reponse_table["new_employee_non_guaranteed_non_binary_percent"] = (
            ne_ng_nb_percent
        )
        new_employee_reponse_table["new_employee_non_guaranteed_30_percent"] = (
            ne_ng_30_pc
        )
        new_employee_reponse_table["new_employee_non_guaranteed_30-50_percent"] = (
            ne_ng_30_50_pc
        )
        new_employee_reponse_table["new_employee_non_guaranteed_50_percent"] = (
            ne_ng_50_pc
        )
        new_employee_reponse_table["new_employee_non_guaranteed_total"] = total_ng

        # new_employee full time

        if dp_employ_full_time:
            dp_employ_full_time_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_full_time]
            )
        else:
            dp_employ_full_time_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        ne_male_ft_qs = dp_employ_full_time_qs.filter(
            index=0, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_female_ft_qs = dp_employ_full_time_qs.filter(
            index=1, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_nb_ft_qs = dp_employ_full_time_qs.filter(
            index=2, metric_name="total"
        ).aggregate(Sum("number_holder"))

        ne_ft_30_qs = dp_employ_full_time_qs.filter(metric_name="yearsold30").aggregate(
            Sum("number_holder")
        )
        ne_ft_30_50_qs = dp_employ_full_time_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        ne_ft_50_qs = dp_employ_full_time_qs.filter(metric_name="yearsold50").aggregate(
            Sum("number_holder")
        )

        total_ft = (
            get_value(ne_male_ft_qs["number_holder__sum"])
            + get_value(ne_female_ft_qs["number_holder__sum"])
            + get_value(ne_nb_ft_qs["number_holder__sum"])
        )

        ne_ft_male_percent = safe_divide_percentage(
            get_value(ne_male_ft_qs["number_holder__sum"]), total_ft
        )
        ne_ft_female_percent = safe_divide_percentage(
            get_value(ne_female_ft_qs["number_holder__sum"]), total_ft
        )
        ne_ft_nb_percent = safe_divide_percentage(
            get_value(ne_nb_ft_qs["number_holder__sum"]), total_ft
        )
        ne_ft_30_pc = safe_divide_percentage(
            get_value(ne_ft_30_qs["number_holder__sum"]), total_ft
        )
        ne_ft_30_50_pc = safe_divide_percentage(
            get_value(ne_ft_30_50_qs["number_holder__sum"]), total_ft
        )
        ne_ft_50_pc = safe_divide_percentage(
            get_value(ne_ft_50_qs["number_holder__sum"]), total_ft
        )

        new_employee_reponse_table["new_employee_full_time_male_percent"] = (
            ne_ft_male_percent
        )
        new_employee_reponse_table["new_employee_full_time_female_percent"] = (
            ne_ft_female_percent
        )
        new_employee_reponse_table["new_employee_full_time_non_binary_percent"] = (
            ne_ft_nb_percent
        )
        new_employee_reponse_table["new_employee_full_time_30_percent"] = ne_ft_30_pc
        new_employee_reponse_table["new_employee_full_time_30-50_percent"] = (
            ne_ft_30_50_pc
        )
        new_employee_reponse_table["new_employee_full_time_50_percent"] = ne_ft_50_pc
        new_employee_reponse_table["new_employee_full_time_total"] = total_ft
        # new_employee part time

        if dp_employ_part_time:
            dp_employ_part_time_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_part_time]
            )
        else:
            dp_employ_part_time_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        ne_male_pt_qs = dp_employ_part_time_qs.filter(
            index=0, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_female_pt_qs = dp_employ_part_time_qs.filter(
            index=1, metric_name="total"
        ).aggregate(Sum("number_holder"))
        ne_nb_pt_qs = dp_employ_part_time_qs.filter(
            index=2, metric_name="total"
        ).aggregate(Sum("number_holder"))

        ne_pt_30_qs = dp_employ_part_time_qs.filter(metric_name="yearsold30").aggregate(
            Sum("number_holder")
        )
        ne_pt_30_50_qs = dp_employ_part_time_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        ne_pt_50_qs = dp_employ_part_time_qs.filter(metric_name="yearsold50").aggregate(
            Sum("number_holder")
        )

        total_pt = (
            get_value(ne_male_pt_qs["number_holder__sum"])
            + get_value(ne_female_pt_qs["number_holder__sum"])
            + get_value(ne_nb_pt_qs["number_holder__sum"])
        )

        ne_pt_male_percent = safe_divide_percentage(
            get_value(ne_male_pt_qs["number_holder__sum"]), total_pt
        )
        ne_pt_female_percent = safe_divide_percentage(
            get_value(ne_female_pt_qs["number_holder__sum"]), total_pt
        )
        ne_pt_nb_percent = safe_divide_percentage(
            get_value(ne_nb_pt_qs["number_holder__sum"]), total_pt
        )
        ne_pt_30_pc = safe_divide_percentage(
            get_value(ne_pt_30_qs["number_holder__sum"]), total_pt
        )
        ne_pt_30_50_pc = safe_divide_percentage(
            get_value(ne_pt_30_50_qs["number_holder__sum"]), total_pt
        )
        ne_pt_50_pc = safe_divide_percentage(
            get_value(ne_pt_50_qs["number_holder__sum"]), total_pt
        )

        new_employee_reponse_table["new_employee_part_time_male_percent"] = (
            ne_pt_male_percent
        )
        new_employee_reponse_table["new_employee_part_time_female_percent"] = (
            ne_pt_female_percent
        )
        new_employee_reponse_table["new_employee_part_time_non_binary_percent"] = (
            ne_pt_nb_percent
        )
        new_employee_reponse_table["new_employee_part_time_30_percent"] = ne_pt_30_pc
        new_employee_reponse_table["new_employee_part_time_30-50_percent"] = (
            ne_pt_30_50_pc
        )
        new_employee_reponse_table["new_employee_part_time_50_percent"] = ne_pt_50_pc
        new_employee_reponse_table["new_employee_part_time_total"] = total_pt
        # employee Turnover Response table

        dp_employ_to_full_time = []
        dp_employ_to_temporary = []
        dp_employ_to_non_guaranteed = []
        dp_employ_to_part_time = []
        dp_employ_to_permanent = []

        for dp in emp_turnover_dps:
            if dp.path.slug == self.employee_turnover_paths["permanent"]:
                dp_employ_to_permanent.append(dp)
            if dp.path.slug == self.employee_turnover_paths["temporary"]:
                dp_employ_to_temporary.append(dp)
            if dp.path.slug == self.employee_turnover_paths["nonguaranteed"]:
                dp_employ_to_non_guaranteed.append(dp)
            if dp.path.slug == self.employee_turnover_paths["fulltime"]:
                dp_employ_to_full_time.append(dp)
            if dp.path.slug == self.employee_turnover_paths["parttime"]:
                dp_employ_to_part_time.append(dp)

        # new_employee_turnover_permanent

        if dp_employ_to_permanent:
            dp_employ_to_permanent_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_to_permanent]
            )
        else:
            dp_employ_to_permanent_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        dp_male_end = dp_employ_to_permanent_qs.filter(
            index=0, metric_name="end"
        ).aggregate(s=Sum("number_holder"))["s"]
        dp_male_beginning = dp_employ_to_permanent_qs.filter(
            index=0, metric_name="beginning"
        ).aggregate(s=Sum("number_holder"))["s"]
        et_male_permanent_qs = get_value(dp_male_end) + get_value(dp_male_beginning)

        dp_female_end = dp_employ_to_permanent_qs.filter(
            index=1, metric_name="end"
        ).aggregate(s=Sum("number_holder"))["s"]
        dp_female_beginning = dp_employ_to_permanent_qs.filter(
            index=1, metric_name="beginning"
        ).aggregate(s=Sum("number_holder"))["s"]
        et_female_permanent_qs = get_value(dp_female_end) + get_value(
            dp_female_beginning
        )

        dp_nb_end = dp_employ_to_permanent_qs.filter(
            index=2, metric_name="end"
        ).aggregate(s=Sum("number_holder"))["s"]
        dp_nb_beginning = dp_employ_to_permanent_qs.filter(
            index=2, metric_name="beginning"
        ).aggregate(s=Sum("number_holder"))["s"]
        et_nb_permanent_qs = get_value(dp_nb_end) + get_value(dp_nb_beginning)

        et_permanent_30_qs = dp_employ_to_permanent_qs.filter(
            metric_name="yearsold30"
        ).aggregate(Sum("number_holder"))
        et_permanent_30_50_qs = dp_employ_to_permanent_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        et_permanent_50_qs = dp_employ_to_permanent_qs.filter(
            metric_name="yearsold50"
        ).aggregate(Sum("number_holder"))

        # * Total Number of employees
        total_permanent_eto = (
            get_value(et_male_permanent_qs)
            + get_value(et_female_permanent_qs)
            + get_value(et_nb_permanent_qs)
        )

        et_per_male_percent = safe_divide_percentage(
            get_value(et_male_permanent_qs),
            total_permanent_eto,
        )
        et_per_female_percent = safe_divide_percentage(
            get_value(et_female_permanent_qs),
            total_permanent_eto,
        )
        et_per_nb_percent = safe_divide_percentage(
            get_value(et_nb_permanent_qs), total_permanent_eto
        )
        et_permanent_30_pc = safe_divide_percentage(
            get_value(et_permanent_30_qs["number_holder__sum"]), total_permanent_eto
        )
        et_permanent_30_50_pc = safe_divide_percentage(
            get_value(et_permanent_30_50_qs["number_holder__sum"]),
            total_permanent_eto,
        )
        et_permanent_50_pc = safe_divide_percentage(
            get_value(et_permanent_50_qs["number_holder__sum"]), total_permanent_eto
        )

        employee_turnover_reponse_table["employee_turnover_permanent_male_percent"] = (
            et_per_male_percent
        )
        employee_turnover_reponse_table[
            "employee_turnover_permanent_female_percent"
        ] = et_per_female_percent
        employee_turnover_reponse_table[
            "employee_turnover_permanent_non_binary_percent"
        ] = et_per_nb_percent
        employee_turnover_reponse_table["employee_turnover_permanent_30_percent"] = (
            et_permanent_30_pc
        )
        employee_turnover_reponse_table["employee_turnover_permanent_30-50_percent"] = (
            et_permanent_30_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_permanent_50_percent"] = (
            et_permanent_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_total"] = total_permanent_eto

        # new_employee_turnover_temporary

        if dp_employ_to_temporary:
            dp_employ_to_temporary_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_to_temporary]
            )
        else:
            dp_employ_to_temporary_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        et_male_temporary_beginning_qs = get_value(
            dp_employ_to_temporary_qs.filter(
                index=0, metric_name="beginning"
            ).aggregate(Sum("number_holder"))["number_holder__sum"]
        )
        et_male_temporary_end_qs = get_value(
            dp_employ_to_temporary_qs.filter(index=0, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_temporary_qs = et_male_temporary_beginning_qs + et_male_temporary_end_qs

        et_female_temporary_beginning_qs = get_value(
            dp_employ_to_temporary_qs.filter(
                index=1, metric_name="beginning"
            ).aggregate(Sum("number_holder"))["number_holder__sum"]
        )

        et_female_temporary_end_qs = get_value(
            dp_employ_to_temporary_qs.filter(index=1, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )
        et_female_temporary_qs = (
            et_female_temporary_beginning_qs + et_female_temporary_end_qs
        )

        et_nb_temporary_beginning_qs = get_value(
            dp_employ_to_temporary_qs.filter(
                index=2, metric_name="beginning"
            ).aggregate(Sum("number_holder"))["number_holder__sum"]
        )

        et_nb_temporary_end_qs = get_value(
            dp_employ_to_temporary_qs.filter(index=2, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_nb_temporary_qs = et_nb_temporary_beginning_qs + et_nb_temporary_end_qs

        et_temporary_30_qs = dp_employ_to_temporary_qs.filter(
            metric_name="yearsold30"
        ).aggregate(Sum("number_holder"))
        et_temporary_30_50_qs = dp_employ_to_temporary_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        et_temporary_50_qs = dp_employ_to_temporary_qs.filter(
            metric_name="yearsold50"
        ).aggregate(Sum("number_holder"))

        total_temporary_eto = (
            get_value(et_male_temporary_qs)
            + get_value(et_female_temporary_qs)
            + get_value(et_nb_temporary_qs)
        )

        et_temp_male_percent = safe_divide_percentage(
            get_value(et_male_temporary_qs),
            total_temporary_eto,
        )
        et_temp_female_percent = safe_divide_percentage(
            get_value(et_female_temporary_qs),
            total_temporary_eto,
        )
        et_temp_nb_percent = safe_divide_percentage(
            get_value(et_nb_temporary_qs), total_temporary_eto
        )
        et_temp_30_pc = safe_divide_percentage(
            get_value(et_temporary_30_qs["number_holder__sum"]), total_temporary_eto
        )
        et_temp_30_50_pc = safe_divide_percentage(
            get_value(et_temporary_30_50_qs["number_holder__sum"]),
            total_temporary_eto,
        )
        et_temp_50_pc = safe_divide_percentage(
            get_value(et_temporary_50_qs["number_holder__sum"]), total_temporary_eto
        )

        employee_turnover_reponse_table["employee_turnover_temporary_male_percent"] = (
            et_temp_male_percent
        )
        employee_turnover_reponse_table[
            "employee_turnover_temporary_female_percent"
        ] = et_temp_female_percent
        employee_turnover_reponse_table[
            "employee_turnover_temporary_non_binary_percent"
        ] = et_temp_nb_percent
        employee_turnover_reponse_table["employee_turnover_temporary_30_percent"] = (
            et_temp_30_pc
        )
        employee_turnover_reponse_table["employee_turnover_temporary_30-50_percent"] = (
            et_temp_30_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_temporary_50_percent"] = (
            et_temp_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_temporary_total"] = (
            total_temporary_eto
        )

        # new_employee_turover _non guaranteed

        if dp_employ_to_non_guaranteed:
            dp_employ_to_ng_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_to_non_guaranteed]
            )
        else:
            dp_employ_to_ng_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        et_male_ng_beginning_qs = get_value(
            dp_employ_to_ng_qs.filter(index=0, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_ng_end_qs = get_value(
            dp_employ_to_ng_qs.filter(index=0, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_ng_qs = et_male_ng_beginning_qs + et_male_ng_end_qs

        et_female_beginning_ng_qs = get_value(
            dp_employ_to_ng_qs.filter(index=1, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_female_end_ng_qs = get_value(
            dp_employ_to_ng_qs.filter(index=1, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_female_ng_qs = et_female_beginning_ng_qs + et_female_end_ng_qs

        et_nb_ng_beginning_qs = get_value(
            dp_employ_to_ng_qs.filter(index=2, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_nb_ng_end_qs = get_value(
            dp_employ_to_ng_qs.filter(index=2, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_nb_ng_qs = et_nb_ng_beginning_qs + et_nb_ng_end_qs

        et_ng_30_qs = dp_employ_to_ng_qs.filter(metric_name="yearsold30").aggregate(
            Sum("number_holder")
        )
        et_ng_30_50_qs = dp_employ_to_ng_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        et_ng_50_qs = dp_employ_to_ng_qs.filter(metric_name="yearsold50").aggregate(
            Sum("number_holder")
        )

        total_ng_eto = (
            get_value(et_male_ng_qs)
            + get_value(et_female_ng_qs)
            + get_value(et_nb_ng_qs)
        )

        et_ng_male_percent = safe_divide_percentage(
            get_value(et_male_ng_qs), total_ng_eto
        )
        et_ng_female_percent = safe_divide_percentage(
            get_value(et_female_ng_qs), total_ng_eto
        )
        et_ng_nb_percent = safe_divide_percentage(get_value(et_nb_ng_qs), total_ng_eto)
        et_ng_30_pc = safe_divide_percentage(
            get_value(et_ng_30_qs["number_holder__sum"]), total_ng_eto
        )
        et_ng_30_50_pc = safe_divide_percentage(
            get_value(et_ng_30_50_qs["number_holder__sum"]), total_ng_eto
        )
        et_ng_50_pc = safe_divide_percentage(
            get_value(et_ng_50_qs["number_holder__sum"]), total_ng_eto
        )

        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_male_percent"
        ] = et_ng_male_percent
        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_female_percent"
        ] = et_ng_female_percent
        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_non_binary_percent"
        ] = et_ng_nb_percent
        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_30_percent"
        ] = et_ng_30_pc
        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_30-50_percent"
        ] = et_ng_30_50_pc
        employee_turnover_reponse_table[
            "employee_turnover_non_guaranteed_50_percent"
        ] = et_ng_50_pc

        # new_employee_turover _full_time

        if dp_employ_to_full_time:
            dp_employ_to_ft_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_to_full_time]
            )
        else:
            dp_employ_to_ft_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        et_male_ft_beginning_qs = get_value(
            dp_employ_to_ft_qs.filter(index=0, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )
        et_male_ft_end_qs = get_value(
            dp_employ_to_ft_qs.filter(index=0, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_ft_qs = et_male_ft_beginning_qs + et_male_ft_end_qs

        et_female_ft_beginning_qs = get_value(
            dp_employ_to_ft_qs.filter(index=1, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_female_ft_end_qs = get_value(
            dp_employ_to_ft_qs.filter(index=1, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_female_ft_qs = et_female_ft_beginning_qs + et_female_ft_end_qs

        et_nb_ft_beginning_qs = get_value(
            dp_employ_to_ft_qs.filter(index=2, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_nb_ft_end_qs = get_value(
            dp_employ_to_ft_qs.filter(index=2, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_nb_ft_qs = et_nb_ft_beginning_qs + et_nb_ft_end_qs

        et_ft_30_qs = dp_employ_to_ft_qs.filter(metric_name="yearsold30").aggregate(
            Sum("number_holder")
        )
        et_ft_30_50_qs = dp_employ_to_ft_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        et_ft_50_qs = dp_employ_to_ft_qs.filter(metric_name="yearsold50").aggregate(
            Sum("number_holder")
        )

        total_ft_eto = (
            get_value(et_male_ft_qs)
            + get_value(et_female_ft_qs)
            + get_value(et_nb_ft_qs)
        )

        et_ft_male_percent = safe_divide_percentage(
            get_value(et_male_ft_qs), total_ft_eto
        )
        et_ft_female_percent = safe_divide_percentage(
            get_value(et_female_ft_qs), total_ft_eto
        )
        et_ft_nb_percent = safe_divide_percentage(get_value(et_nb_ft_qs), total_ft_eto)
        et_ft_30_pc = safe_divide_percentage(
            get_value(et_ft_30_qs["number_holder__sum"]), total_ft_eto
        )
        et_ft_30_50_pc = safe_divide_percentage(
            get_value(et_ft_30_50_qs["number_holder__sum"]), total_ft_eto
        )
        et_ft_50_pc = safe_divide_percentage(
            get_value(et_ft_50_qs["number_holder__sum"]), total_ft_eto
        )

        employee_turnover_reponse_table["employee_turnover_full_time_male_percent"] = (
            et_ft_male_percent
        )
        employee_turnover_reponse_table[
            "employee_turnover_full_time_female_percent"
        ] = et_ft_female_percent
        employee_turnover_reponse_table[
            "employee_turnover_full_time_non_binary_percent"
        ] = et_ft_nb_percent
        employee_turnover_reponse_table["employee_turnover_full_time_30_percent"] = (
            et_ft_30_pc
        )
        employee_turnover_reponse_table["employee_turnover_full_time_30-50_percent"] = (
            et_ft_30_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_full_time_50_percent"] = (
            et_ft_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_total"] = total_ft_eto

        # new_employee_turover _parttime

        if dp_employ_to_part_time:
            dp_employ_to_pt_qs = DataPoint.objects.filter(
                id__in=[dp.id for dp in dp_employ_to_part_time]
            )
        else:
            dp_employ_to_pt_qs = (
                DataPoint.objects.none()
            )  # Assuming DataPoint is your model

        et_male_pt_beginning_qs = get_value(
            dp_employ_to_pt_qs.filter(index=0, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_pt_end_qs = get_value(
            dp_employ_to_pt_qs.filter(index=0, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_male_pt_qs = et_male_pt_beginning_qs + et_male_pt_end_qs

        et_female_pt_beginning_qs = get_value(
            dp_employ_to_pt_qs.filter(index=1, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )

        et_female_pt_end_qs = get_value(
            dp_employ_to_pt_qs.filter(index=1, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )
        et_female_pt_qs = et_female_pt_beginning_qs + et_female_pt_end_qs

        et_nb_pt_beginning_qs = get_value(
            dp_employ_to_pt_qs.filter(index=2, metric_name="beginning").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )
        et_nb_pt_end_qs = get_value(
            dp_employ_to_pt_qs.filter(index=2, metric_name="end").aggregate(
                Sum("number_holder")
            )["number_holder__sum"]
        )
        et_nb_pt_qs = et_nb_pt_beginning_qs + et_nb_pt_end_qs

        et_pt_30_qs = dp_employ_to_pt_qs.filter(metric_name="yearsold30").aggregate(
            Sum("number_holder")
        )
        et_pt_30_50_qs = dp_employ_to_pt_qs.filter(
            metric_name="yearsold30to50"
        ).aggregate(Sum("number_holder"))
        et_pt_50_qs = dp_employ_to_pt_qs.filter(metric_name="yearsold50").aggregate(
            Sum("number_holder")
        )

        total_pt_eto = (
            get_value(et_male_pt_qs)
            + get_value(et_female_pt_qs)
            + get_value(et_nb_pt_qs)
        )

        et_pt_male_percent = safe_divide_percentage(
            get_value(et_male_pt_qs), total_pt_eto
        )
        et_pt_female_percent = safe_divide_percentage(
            get_value(et_female_pt_qs), total_pt_eto
        )
        et_pt_nb_percent = safe_divide_percentage(get_value(et_nb_pt_qs), total_pt_eto)
        et_pt_30_pc = safe_divide_percentage(
            get_value(et_pt_30_qs["number_holder__sum"]), total_pt_eto
        )
        et_pt_30_50_pc = safe_divide_percentage(
            get_value(et_pt_30_50_qs["number_holder__sum"]), total_pt_eto
        )
        et_pt_50_pc = safe_divide_percentage(
            get_value(et_pt_50_qs["number_holder__sum"]), total_pt_eto
        )

        employee_turnover_reponse_table["employee_turnover_part_time_male_percent"] = (
            et_pt_male_percent
        )
        employee_turnover_reponse_table[
            "employee_turnover_part_time_female_percent"
        ] = et_pt_female_percent
        employee_turnover_reponse_table[
            "employee_turnover_part_time_non_binary_percent"
        ] = et_pt_nb_percent
        employee_turnover_reponse_table["employee_turnover_part_time_30_percent"] = (
            et_pt_30_pc
        )
        employee_turnover_reponse_table["employee_turnover_part_time_30-50_percent"] = (
            et_pt_30_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_part_time_50_percent"] = (
            et_pt_50_pc
        )
        employee_turnover_reponse_table["employee_turnover_total"] = total_pt_eto

        benefits_dps = benefits_data_points

        # parental leave first

        parental_leave_response_table["entitlement_male"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=0, metric_name="male").first()
            )
        )
        parental_leave_response_table["entitlement_female"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=0, metric_name="female").first()
            )
        )
        parental_leave_response_table["entitlement_total"] = (
            parental_leave_response_table["entitlement_male"]
            + parental_leave_response_table["entitlement_female"]
        )

        parental_leave_response_table["taking_male"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=1, metric_name="male").first()
            )
        )
        parental_leave_response_table["taking_female"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=1, metric_name="female").first()
            )
        )
        parental_leave_response_table["taking_total"] = (
            parental_leave_response_table["taking_male"]
            + parental_leave_response_table["taking_female"]
        )

        parental_leave_response_table["return_to_post_work_male"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=2, metric_name="male").first()
            )
        )
        parental_leave_response_table["return_to_post_work_female"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=2, metric_name="female").first()
            )
        )
        parental_leave_response_table["return_to_post_work_total"] = (
            parental_leave_response_table["return_to_post_work_male"]
            + parental_leave_response_table["return_to_post_work_female"]
        )

        parental_leave_response_table["retained_12_mts_male"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=3, metric_name="male").first()
            )
        )
        parental_leave_response_table["retained_12_mts_female"] = get_integer(
            get_object_value(
                parental_leave_data_points.filter(index=3, metric_name="female").first()
            )
        )
        parental_leave_response_table["retained_12_mts_total"] = (
            parental_leave_response_table["retained_12_mts_male"]
            + parental_leave_response_table["retained_12_mts_female"]
        )

        # benefits table

        # Show by latest month in the date range
        # It is supposed to anually but we are currently collecting it monthly.
        benefits_response_table["life_insurance_full_time"] = get_object_value(
            benefits_dps.filter(index=0, metric_name="fulltime").first()
        )
        benefits_response_table["life_insurance_part_time"] = get_object_value(
            benefits_dps.filter(index=0, metric_name="parttime").first()
        )
        benefits_response_table["life_insurance_temporary"] = get_object_value(
            benefits_dps.filter(index=0, metric_name="temporary").first()
        )
        benefits_response_table["life_insurance_significant_location"] = (
            get_object_value(
                benefits_dps.filter(index=0, metric_name="significantlocation").first()
            )
        )

        benefits_response_table["healthcare_full_time"] = get_object_value(
            benefits_dps.filter(index=1, metric_name="fulltime").first()
        )
        benefits_response_table["healthcare_part_time"] = get_object_value(
            benefits_dps.filter(index=1, metric_name="parttime").first()
        )
        benefits_response_table["healthcare_temporary"] = get_object_value(
            benefits_dps.filter(index=1, metric_name="temporary").first()
        )
        benefits_response_table["healthcare_significant_location"] = get_object_value(
            benefits_dps.filter(index=1, metric_name="significantlocation").first()
        )

        benefits_response_table["disability_cover_full_time"] = get_object_value(
            benefits_dps.filter(index=2, metric_name="fulltime").first()
        )
        benefits_response_table["disability_cover_part_time"] = get_object_value(
            benefits_dps.filter(index=2, metric_name="parttime").first()
        )
        benefits_response_table["disability_cover_temporary"] = get_object_value(
            benefits_dps.filter(index=2, metric_name="temporary").first()
        )
        benefits_response_table["disability_cover_significant_location"] = (
            get_object_value(
                benefits_dps.filter(index=2, metric_name="significantlocation").first()
            )
        )

        benefits_response_table["parental_leave_full_time"] = get_object_value(
            benefits_dps.filter(index=3, metric_name="fulltime").first()
        )
        benefits_response_table["parental_leave_part_time"] = get_object_value(
            benefits_dps.filter(index=3, metric_name="parttime").first()
        )
        benefits_response_table["parental_leave_temporary"] = get_object_value(
            benefits_dps.filter(index=3, metric_name="temporary").first()
        )
        benefits_response_table["parental_leave_significant_location"] = (
            get_object_value(
                benefits_dps.filter(index=3, metric_name="significantlocation").first()
            )
        )

        benefits_response_table["retirement_full_time"] = get_object_value(
            benefits_dps.filter(index=4, metric_name="fulltime").first()
        )
        benefits_response_table["retirement_part_time"] = get_object_value(
            benefits_dps.filter(index=4, metric_name="parttime").first()
        )
        benefits_response_table["retirement_temporary"] = get_object_value(
            benefits_dps.filter(index=4, metric_name="temporary").first()
        )
        benefits_response_table["retirement_significant_location"] = get_object_value(
            benefits_dps.filter(index=4, metric_name="significantlocation").first()
        )

        benefits_response_table["stock_ownership_full_time"] = get_object_value(
            benefits_dps.filter(index=5, metric_name="fulltime").first()
        )
        benefits_response_table["stock_ownership_part_time"] = get_object_value(
            benefits_dps.filter(index=5, metric_name="parttime").first()
        )
        benefits_response_table["stock_ownership_temporary"] = get_object_value(
            benefits_dps.filter(index=5, metric_name="temporary").first()
        )
        benefits_response_table["stock_ownership_significant_location"] = (
            get_object_value(
                benefits_dps.filter(index=5, metric_name="significantlocation").first()
            )
        )
        benefits_response_table["extra_benefits"] = []
        # * Get extra fields that have index more than 5
        for i in (
            benefits_dps.order_by("index").values_list("index", flat=True).distinct()
        ):
            benefits_response_table["extra_benefits"].append(
                {
                    "benefits": get_object_value(
                        benefits_dps.filter(index=i, metric_name="benefits").first()
                    ),
                    "full_time": get_object_value(
                        benefits_dps.filter(index=i, metric_name="fulltime").first()
                    ),
                    "part_time": get_object_value(
                        benefits_dps.filter(index=i, metric_name="parttime").first()
                    ),
                    "temporary": get_object_value(
                        benefits_dps.filter(index=i, metric_name="temporary").first()
                    ),
                    "significant_location": get_object_value(
                        benefits_dps.filter(
                            index=i, metric_name="significantlocation"
                        ).first()
                    ),
                }
            )

        benefits_response_table["benefits_full_time_employees"] = (
            collect_data_by_raw_response_and_index(
                benefits_dps.filter(path__slug=self.employee_benefits_path_slugs[1])
            )
        )
        benefits_response_table["benefits_part_time_employees"] = (
            collect_data_by_raw_response_and_index(
                benefits_dps.filter(path__slug=self.employee_benefits_path_slugs[2])
            )
        )
        benefits_response_table["benefits_temporary_employees"] = (
            collect_data_by_raw_response_and_index(
                benefits_dps.filter(path__slug=self.employee_benefits_path_slugs[3])
            )
        )

        return (
            new_employee_reponse_table,
            employee_turnover_reponse_table,
            benefits_response_table,
            parental_leave_response_table,
        )

    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate and Year"""

        # * Get all the RawResponses
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data["organisation"]
        self.location = serializer.validated_data.get("location")  # * This is optional

        client_id = request.user.client.id
        new_emp_data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.new_employee_hire_path_slugs,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        )
        emp_turnover_data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.employee_turnover_path_slugs,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        )
        benefits_data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.employee_benefits_path_slugs,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .order_by("-year", "-month")
        )
        parental_leave_data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.employee_parental_leave_path_slugs,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .order_by("-year", "-month")
        )
        # pushing for processing
        (
            new_employee_reponse_table,
            _,
            benefits_response_table,
            parental_leave_response_table,
        ) = self.process_dataPoints(
            new_emp_data_points,
            emp_turnover_data_points,
            benefits_data_points,
            parental_leave_data_points,
        )
        # * Get top emissions by Scope
        response_data = dict()
        response_data["success_true"] = "true"

        response_data["new_employee_hires"] = []

        new_employee_permanent = {}
        new_employee_permanent["type_of_employee"] = "Permanent employee"
        new_employee_permanent["percentage_of_male_employee"] = (
            new_employee_reponse_table["new_employee_permanent_male_percent"]
        )
        new_employee_permanent["percentage_of_female_employee"] = (
            new_employee_reponse_table["new_employee_permanent_female_percent"]
        )
        new_employee_permanent["percentage_of_non_binary_employee"] = (
            new_employee_reponse_table["new_employee_permanent_non_binary_percent"]
        )
        new_employee_permanent["yearsold30"] = new_employee_reponse_table[
            "new_employee_permanent_30_percent"
        ]
        new_employee_permanent["yearsold50"] = new_employee_reponse_table[
            "new_employee_permanent_50_percent"
        ]
        new_employee_permanent["yearsold30to50"] = new_employee_reponse_table[
            "new_employee_permanent_30-50_percent"
        ]
        new_employee_permanent["total"] = new_employee_reponse_table[
            "new_employee_permanent_total"
        ]
        response_data["new_employee_hires"].append(new_employee_permanent)

        new_employee_temporary = {}
        new_employee_temporary["type_of_employee"] = "Temporary employee"
        new_employee_temporary["percentage_of_male_employee"] = (
            new_employee_reponse_table["new_employee_temporary_male_percent"]
        )
        new_employee_temporary["percentage_of_female_employee"] = (
            new_employee_reponse_table["new_employee_temporary_female_percent"]
        )
        new_employee_temporary["percentage_of_non_binary_employee"] = (
            new_employee_reponse_table["new_employee_temporary_non_binary_percent"]
        )
        new_employee_temporary["yearsold30"] = new_employee_reponse_table[
            "new_employee_temporary_30_percent"
        ]
        new_employee_temporary["yearsold50"] = new_employee_reponse_table[
            "new_employee_temporary_50_percent"
        ]
        new_employee_temporary["yearsold30to50"] = new_employee_reponse_table[
            "new_employee_temporary_30-50_percent"
        ]
        new_employee_temporary["total"] = new_employee_reponse_table[
            "new_employee_temporary_total"
        ]
        response_data["new_employee_hires"].append(new_employee_temporary)

        new_employee_non_guaranteed = {}
        new_employee_non_guaranteed["type_of_employee"] = "Non guaranteed employee"
        new_employee_non_guaranteed["percentage_of_male_employee"] = (
            new_employee_reponse_table["new_employee_non_guaranteed_male_percent"]
        )
        new_employee_non_guaranteed["percentage_of_female_employee"] = (
            new_employee_reponse_table["new_employee_non_guaranteed_female_percent"]
        )
        new_employee_non_guaranteed["percentage_of_non_binary_employee"] = (
            new_employee_reponse_table["new_employee_non_guaranteed_non_binary_percent"]
        )
        new_employee_non_guaranteed["yearsold30"] = new_employee_reponse_table[
            "new_employee_non_guaranteed_30_percent"
        ]
        new_employee_non_guaranteed["yearsold50"] = new_employee_reponse_table[
            "new_employee_non_guaranteed_30-50_percent"
        ]
        new_employee_non_guaranteed["yearsold30to50"] = new_employee_reponse_table[
            "new_employee_temporary_30-50_percent"
        ]
        new_employee_non_guaranteed["total"] = new_employee_reponse_table[
            "new_employee_non_guaranteed_total"
        ]
        response_data["new_employee_hires"].append(new_employee_non_guaranteed)

        new_employee_full_time = {}
        new_employee_full_time["type_of_employee"] = "Full Time employee"
        new_employee_full_time["percentage_of_male_employee"] = (
            new_employee_reponse_table["new_employee_full_time_male_percent"]
        )
        new_employee_full_time["percentage_of_female_employee"] = (
            new_employee_reponse_table["new_employee_full_time_female_percent"]
        )
        new_employee_full_time["percentage_of_non_binary_employee"] = (
            new_employee_reponse_table["new_employee_full_time_non_binary_percent"]
        )
        new_employee_full_time["yearsold30"] = new_employee_reponse_table[
            "new_employee_full_time_30_percent"
        ]
        new_employee_full_time["yearsold50"] = new_employee_reponse_table[
            "new_employee_full_time_30-50_percent"
        ]
        new_employee_full_time["yearsold30to50"] = new_employee_reponse_table[
            "new_employee_full_time_50_percent"
        ]
        new_employee_full_time["total"] = new_employee_reponse_table[
            "new_employee_full_time_total"
        ]
        response_data["new_employee_hires"].append(new_employee_full_time)

        new_employee_part_time = {}
        new_employee_part_time["type_of_employee"] = "Part time employee"
        new_employee_part_time["percentage_of_male_employee"] = (
            new_employee_reponse_table["new_employee_part_time_male_percent"]
        )
        new_employee_part_time["percentage_of_female_employee"] = (
            new_employee_reponse_table["new_employee_part_time_female_percent"]
        )
        new_employee_part_time["percentage_of_non_binary_employee"] = (
            new_employee_reponse_table["new_employee_part_time_non_binary_percent"]
        )
        new_employee_part_time["yearsold30"] = new_employee_reponse_table[
            "new_employee_part_time_30_percent"
        ]
        new_employee_part_time["yearsold50"] = new_employee_reponse_table[
            "new_employee_part_time_30-50_percent"
        ]
        new_employee_part_time["yearsold30to50"] = new_employee_reponse_table[
            "new_employee_part_time_50_percent"
        ]
        new_employee_part_time["total"] = new_employee_reponse_table[
            "new_employee_part_time_total"
        ]
        response_data["new_employee_hires"].append(new_employee_part_time)
        response_data["new_employee_hires"].append(
            {
                "type_of_employee": "Total",
                "total": new_employee_permanent["total"]
                + new_employee_temporary["total"]
                + new_employee_non_guaranteed["total"]
                + new_employee_full_time["total"]
                + new_employee_part_time["total"],
            }
        )
        all_benefits = {
            "benefits_full_time_employees": [],
            "benefits_part_time_employees": [],
            "benefits_temporary_employees": [],
        }

        all_benefits["benefits_full_time_employees"].extend(
            benefits_response_table["benefits_full_time_employees"]
        )
        all_benefits["benefits_part_time_employees"].extend(
            benefits_response_table["benefits_part_time_employees"]
        )
        all_benefits["benefits_temporary_employees"].extend(
            benefits_response_table["benefits_temporary_employees"]
        )
        response_data["employee_turnover"] = self.get_employment_turnover(
            employment_turnover_data_points=emp_turnover_data_points
        )

        response_data["benefits"] = all_benefits

        parental_leave = []
        entitlement = {}
        entitlement["employee_category"] = "Parental Leave Entitlement"
        entitlement["male"] = parental_leave_response_table["entitlement_male"]
        entitlement["female"] = parental_leave_response_table["entitlement_female"]
        entitlement["total"] = parental_leave_response_table["entitlement_total"]
        parental_leave.append(entitlement)

        taking = {}
        taking["employee_category"] = "Taking Parental Leave"
        taking["male"] = parental_leave_response_table["taking_male"]
        taking["female"] = parental_leave_response_table["taking_female"]
        taking["total"] = parental_leave_response_table["taking_total"]
        parental_leave.append(taking)
        # Returning to work Post leave, Retained 12th month after leave

        post_leave = {}
        post_leave["employee_category"] = "Returning to work Post leave"
        post_leave["male"] = parental_leave_response_table["return_to_post_work_male"]
        post_leave["female"] = parental_leave_response_table[
            "return_to_post_work_female"
        ]
        post_leave["total"] = parental_leave_response_table["return_to_post_work_total"]
        parental_leave.append(post_leave)

        retained = {}
        retained["employee_category"] = "Retained 12th month after leave"
        retained["male"] = parental_leave_response_table["retained_12_mts_male"]
        retained["female"] = parental_leave_response_table["retained_12_mts_female"]
        retained["total"] = parental_leave_response_table["retained_12_mts_total"]
        parental_leave.append(retained)

        response_data["parental_leave"] = parental_leave

        # * Return to work rate and retention rate of employee
        return_to_work_rate_and_retention_rate_of_employee = []
        return_to_work_rate = {}
        return_to_work_rate["employee_category"] = "Return to work rate"
        # * Return to work rate = (Total number of employees that did return to work after parental leave)/(Total number of employees due to return to work after taking parental leave)
        return_to_work_rate["male"] = safe_divide_percentage(
            parental_leave_response_table["return_to_post_work_male"],
            parental_leave_response_table["taking_total"],
        )

        return_to_work_rate["female"] = safe_divide_percentage(
            parental_leave_response_table["return_to_post_work_female"],
            parental_leave_response_table["taking_total"],
        )
        return_to_work_rate_and_retention_rate_of_employee.append(return_to_work_rate)

        retention_rate = {}
        retention_rate["employee_category"] = "Retention rate"
        retention_rate["male"] = safe_divide_percentage(
            parental_leave_response_table["retained_12_mts_male"],
            parental_leave_response_table["return_to_post_work_total"],
        )
        retention_rate["female"] = safe_divide_percentage(
            parental_leave_response_table["retained_12_mts_female"],
            parental_leave_response_table["return_to_post_work_total"],
        )
        return_to_work_rate_and_retention_rate_of_employee.append(retention_rate)
        response_data["return_to_work_rate_and_retention_rate_of_employee"] = (
            return_to_work_rate_and_retention_rate_of_employee
        )

        return Response({"data": response_data}, status=status.HTTP_200_OK)
