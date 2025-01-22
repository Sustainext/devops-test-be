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
from datametric.models import RawResponse
from django.db.models.expressions import RawSQL
from django.db.models import Value
from decimal import Decimal
from common.utils.value_types import safe_percentage, safe_divide, format_decimal_places


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
    permission_classes = [IsAuthenticated]

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

    def get_work_related_ill_health(self, number_of_hours):
        slug = "gri-social-ohs-403-9a-number_of_injuries_emp"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            new_data = []
            for item in raw_response.data:
                item["year"] = raw_response.year
                item["month"] = raw_response.month
                new_data.append(item)
            data.extend(new_data)

        for entry in data:
            entry["rate_of_fatalities_as_a_result_of_work_related_injury"] = (
                format_decimal_places(
                    Decimal(
                        safe_divide(
                            int(entry["fatalities"]), int(entry["numberofhoursworked"])
                        )
                    )
                    * number_of_hours
                )
            )
            entry[
                "rate_of_high_consequence_work_related_injuries_excluding_fatalities"
            ] = format_decimal_places(
                Decimal(
                    safe_divide(
                        int(entry["highconsequence"]), int(entry["numberofhoursworked"])
                    )
                )
                * number_of_hours
            )
            entry["rate_of_recordable_work_related_injuries"] = format_decimal_places(
                Decimal(
                    safe_divide(
                        int(entry["recordable"]),
                        int(entry["numberofhoursworked"]),
                    )
                )
                * number_of_hours
            )
        return data

    def get_rate_of_injuries_who_are_workers_but_not_employees(self, number_of_hours):
        slug = "gri-social-ohs-403-9b-number_of_injuries_workers"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            new_data = []
            for item in raw_response.data:
                item["year"] = raw_response.year
                item["month"] = raw_response.month
                new_data.append(item)
            data.extend(new_data)

        for entry in data:
            entry["rate_of_fatalities_as_a_result_of_work_related_injury"] = (
                format_decimal_places(
                    Decimal(
                        safe_divide(
                            int(entry["fatalities"]),
                            int(entry["numberofhoursworked"]),
                        )
                    )
                    * number_of_hours
                )
            )
            entry[
                "rate_of_high_consequence_work_related_injuries_excluding_fatalities"
            ] = format_decimal_places(
                Decimal(
                    safe_divide(
                        int(entry["highconsequence"]),
                        int(entry["numberofhoursworked"]),
                    )
                )
                * number_of_hours
            )
            entry["rate_of_recordable_work_related_injuries"] = format_decimal_places(
                Decimal(
                    safe_divide(
                        int(entry["recordable"]),
                        int(entry["numberofhoursworked"]),
                    )
                )
                * number_of_hours
            )
        return data

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

        return Response(
            {
                "rate_of_injuries_for_all_employees_100_injury_rate": self.get_work_related_ill_health(
                    100
                ),
                "rate_of_injuries_for_not_included_in_company_employees_100_injury_rate": self.get_rate_of_injuries_who_are_workers_but_not_employees(
                    100
                ),
                "rate_of_injuries_for_all_employees_500_injury_rate": self.get_work_related_ill_health(
                    500
                ),
                "rate_of_injuries_for_not_included_in_company_employees_500_injury_rate": self.get_rate_of_injuries_who_are_workers_but_not_employees(
                    500
                ),
            },
            status=status.HTTP_200_OK,
        )
