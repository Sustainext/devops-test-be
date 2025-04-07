from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.permissions import IsAuthenticated
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from datametric.models import RawResponse, DataPoint
from django.db.models.expressions import RawSQL
from django.db.models import Value
from decimal import Decimal
from common.utils.value_types import safe_percentage, safe_divide
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
import datetime
import calendar
from typing import Optional, Dict, Any, cast


class OHSAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.NON_EMPLOYEE_WORKERS_PERCENTAGE = "Percentage of workers who are not employees but whose work and/or workplace is controlled by the organization"
        self.TOTAL_EMPLOYEES_PERCENTAGE = "Percentage of all Employees"

    def set_raw_responses(self):
        slugs = [
            "gri-social-ohs-403-9b-number_of_injuries_workers",
            "gri-social-ohs-403-9e-number_of_hours",
            "gri-social-ohs-403-8a-number_of_employees",
            "gri-social-ohs-403-9a-number_of_injuries_emp",
            "gri-social-ohs-403-10a-ill_health_emp",
            "gri-social-ohs-403-10b-ill_health_workers",
            "gri-social-ohs-403-4d-formal_joint",
        ]
        self.raw_responses = (
            RawResponse.objects.filter(
                path__slug__in=slugs,
                client=self.request.user.client,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .annotate(json_data=RawSQL("CAST(data AS JSONB)", []))
            .exclude(json_data=Value("[]"))
            .only("data")
        )

    def get_formal_joint_management(self):
        slug = "gri-social-ohs-403-4d-formal_joint"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.extend(raw_response.data)
        return data

    def get_workers_covered_by_an_occupational_health_and_safety_management_system(
        self,
    ):
        slug = "gri-social-ohs-403-8a-number_of_employees"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.append(raw_response.data)
        local_response_data = []
        for entry in data:
            total_number_of_employees_covered_by_the_system = sum(
                [int(_["coveredbythesystem"]) for _ in entry]
            )
            total_number_of_internally_audited_workers = sum(
                [int(_["internallyaudited"]) for _ in entry]
            )
            temp = {}
            temp["percentage_of_all_employees_covered_by_the_system"] = safe_percentage(
                int(entry[0]["coveredbythesystem"]),
                total_number_of_employees_covered_by_the_system,
            )
            temp["percentage_of_internally_audited_workers"] = safe_percentage(
                int(entry[0]["internallyaudited"]),
                total_number_of_internally_audited_workers,
            )
            temp["percentage_of_all_employees_internally_audited"] = safe_percentage(
                int(entry[1]["coveredbythesystem"]),
                total_number_of_employees_covered_by_the_system,
            )
            temp["percentage_of_workers_who_are_not_emplyees_internally_audited"] = (
                safe_percentage(
                    int(entry[1]["internallyaudited"]),
                    total_number_of_internally_audited_workers,
                )
            )
            temp["percentage_of_all_employees_externally_audited"] = safe_percentage(
                int(entry[2]["coveredbythesystem"]),
                total_number_of_employees_covered_by_the_system,
            )
            temp["percentage_of_workers_who_are_not_emplyees_externally_audited"] = (
                safe_percentage(
                    int(entry[2]["internallyaudited"]),
                    total_number_of_internally_audited_workers,
                )
            )
            local_response_data.append(temp)
        return self.convert_ohs_data_as_per_frontend_response(local_response_data)

    def get_ill_health_for_all_employees_analysis(self):
        slug = "gri-social-ohs-403-10a-ill_health_emp"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.extend(raw_response.data)
        return data

    def get_ill_health_for_all_workers_who_are_not_employees_analysis(self):
        slug = "gri-social-ohs-403-10b-ill_health_workers"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.extend(raw_response.data)
        return data

    def get_number_of_hours_worked(self):
        slug = "gri-social-ohs-403-9e-number_of_hours"
        local_raw_response = self.raw_responses.filter(path__slug=slug).order_by(
            "month", "year"
        )
        return local_raw_response

    def convert_ohs_data_as_per_frontend_response(self, data):
        if len(data) == 0:
            return []

        original_data = data[0]

        response = [
            {
                "": "Covered by the system",
                self.TOTAL_EMPLOYEES_PERCENTAGE: f"{str(original_data.get('percentage_of_all_employees_covered_by_the_system', 0))}%",
                self.NON_EMPLOYEE_WORKERS_PERCENTAGE: f"{original_data.get('percentage_of_internally_audited_workers', 0)}%",
            },
            {
                "": "Internally audited",
                self.TOTAL_EMPLOYEES_PERCENTAGE: f"{original_data.get('percentage_of_all_employees_internally_audited', 0)}%",
                self.NON_EMPLOYEE_WORKERS_PERCENTAGE: f"{original_data.get('percentage_of_workers_who_are_not_emplyees_internally_audited', 0)}%",
            },
            {
                "": "Audited or certified by an external party.",
                self.TOTAL_EMPLOYEES_PERCENTAGE: f"{original_data.get('percentage_of_all_employees_externally_audited', 0)}%",
                self.NON_EMPLOYEE_WORKERS_PERCENTAGE: f"{original_data.get('percentage_of_workers_who_are_not_emplyees_externally_audited', 0)}%",
            },
        ]

        return response

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data.get("organisation")
        self.location = serializer.validated_data.get("location")  # * This is optional
        self.set_raw_responses()

        response_data = {
            "formal_joint_management": self.get_formal_joint_management(),
            "workers_covered_by_an_occupational_health_and_safety_management_system": self.get_workers_covered_by_an_occupational_health_and_safety_management_system(),
            "ill_health_for_all_employees_analysis": self.get_ill_health_for_all_employees_analysis(),
            "ill_health_for_all_workers_who_are_not_employees_analysis": self.get_ill_health_for_all_workers_who_are_not_employees_analysis(),
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GetIllnessAnalysisView(APIView):
    start: datetime.date
    end: datetime.date
    permission_classes = [IsAuthenticated]
    INJURY_RATE_DICT = {100: 2_00_000, 500: 10_00_000}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slugs = {
            0: "gri-social-ohs-403-9a-number_of_injuries_emp",
            1: "gri-social-ohs-403-9b-number_of_injuries_workers",
        }
        self.warning_message = None


    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(
                client_id=self.request.user.client.id,
            )
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        ).filter(path__slug__in=list(self.slugs.values()))

    def get_work_related_ill_health(self, number_of_hours, slug):
        local_data_points = self.data_points.filter(path__slug=slug)
        data = collect_data_by_raw_response_and_index(local_data_points)
        total = {
            "fatalities": Decimal(0),
            "numberofhoursworked": Decimal(0),
            "recordable": Decimal(0),
            "highconsequence": Decimal(0),
        }
        for i in data:
            total["fatalities"] += Decimal(i.get("fatalities", 0))
            total["numberofhoursworked"] += Decimal(i.get("numberofhoursworked", 0))
            total["recordable"] += Decimal(i.get("recordable", 0))
            total["highconsequence"] += Decimal(i.get("highconsequence", 0))
        local_response = [
            {
                "rate_of_fatalities_as_a_result_of_work_related_injury": safe_divide(
                    (total["fatalities"] * number_of_hours),
                    total["numberofhoursworked"],
                ),
                "rate_of_high_consequence_work_related_injuries_excluding_fatalities": safe_divide(
                    (total["recordable"] * number_of_hours),
                    total["numberofhoursworked"],
                ),
                "rate_of_recordable_work_related_injuries": safe_divide(
                    (total["highconsequence"] * number_of_hours),
                    total["numberofhoursworked"],
                ),
            }
        ]
        return local_response

    def get_months_difference(self):
        """Calculate number of months between start and end dates"""
        months_difference = (
            (self.end.year - self.start.year) * 12
            + (self.end.month - self.start.month)
            + 1
        )
        return months_difference
    def get_months_years_optimized(self):
        """
        Generates a set of unique (month, year) tuples by iterating month-by-month.

        Returns:
        A set containing tuples of (month, year) integers for each unique
        month/year combination within the range (inclusive).
        Returns an empty set if end_date is before start_date.
        """
        start_date = self.start
        end_date = self.end
        if end_date < start_date:
            return set()

        year_months = set()

        # Start with a marker date at the beginning of the start_date's month
        # This simplifies the loop logic.
        current_marker_date = datetime.date(start_date.year, start_date.month, 1)

        while current_marker_date <= end_date:
        # Add the current marker's month and year
            year_months.add((current_marker_date.year, current_marker_date.month))

            # Calculate the first day of the *next* month
            current_year = current_marker_date.year
            current_month = current_marker_date.month

            if current_month == 12:
                next_month = 1
                next_year = current_year + 1
            else:
                next_month = current_month + 1
                next_year = current_year

            # Check if the next year is valid before creating the date
            if next_year > datetime.MAXYEAR:
                break # Stop if we exceed the maximum representable year

            # Move the marker to the first day of the next month
            current_marker_date = datetime.date(next_year, next_month, 1)

        return year_months

    def are_all_required_months_present_inside_data_points(self):
        # * Get all the months data inside the data points
        months_data = set([(i["year"],i["month"]) for i in self.data_points.values("month", "year")])

        # * Get all the months between start and end dates
        months_between_start_and_end = self.get_months_years_optimized()
        # * Check if all the months between start and end dates are present in the data points
        difference_in_dates = set(months_between_start_and_end) - set(months_data)
        if set(months_between_start_and_end) == set(months_data):
            return True

        minimum_date = min(months_data)
        maximum_date = max(months_data)
        self.warning_message = f"The data is available only for the period {calendar.month_name[minimum_date[1]]} {minimum_date[0]} to {calendar.month_name[maximum_date[1]]} {maximum_date[0]}"
        return False

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data: Dict[str,Any] = cast(Dict[str, Any], serializer.validated_data)
        self.start = data["start"]
        self.end = data["end"]
        self.corporate = data.get("corporate")  # * This is optional
        self.organisation = data.get("organisation")
        self.location = data.get("location")  # * This is optional


        show_warning = False
        self.set_data_points()
        if self.are_all_required_months_present_inside_data_points():
            show_warning = False
        else:
            show_warning = True

        months_difference = self.get_months_difference()
        number_of_hours_for_100_injury_rate = Decimal(
            self.INJURY_RATE_DICT[100] * months_difference / 12
        )

        number_of_hours_for_500_injury_rate = Decimal(
            self.INJURY_RATE_DICT[500] * months_difference / 12
        )
        normal_response = {
            "rate_of_injuries_for_all_employees_100_injury_rate": self.get_work_related_ill_health(
                number_of_hours_for_100_injury_rate,
                slug=self.slugs[0],
            ),
            "rate_of_injuries_for_not_included_in_company_employees_100_injury_rate": self.get_work_related_ill_health(
                number_of_hours_for_100_injury_rate,
                slug=self.slugs[1],
            ),
            "rate_of_injuries_for_all_employees_500_injury_rate": self.get_work_related_ill_health(
                number_of_hours_for_500_injury_rate,
                slug=self.slugs[0],
            ),
            "rate_of_injuries_for_not_included_in_company_employees_500_injury_rate": self.get_work_related_ill_health(
                number_of_hours_for_500_injury_rate,
                slug=self.slugs[1],
            ),
        }

        if not show_warning:
            return Response(
                {
                    "message": "Data retrieved successfully",
                    "data": normal_response,
                    "status": status.HTTP_200_OK,
                },

                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": self.warning_message,
                    "data": normal_response,
                    "status": status.HTTP_206_PARTIAL_CONTENT,
                },
                status=status.HTTP_206_PARTIAL_CONTENT,
            )
