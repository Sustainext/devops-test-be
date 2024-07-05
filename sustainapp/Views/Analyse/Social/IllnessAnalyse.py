from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.permissions import IsAuthenticated
from datametric.utils.analyse import set_locations_data, filter_by_start_end_dates
from datametric.models import RawResponse
import re


class IllnessAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def set_raw_responses(self):
        slugs = [
            "gri-social-ohs-403-4d-formal_joint",
            "gri-social-ohs-403-8a-number_of_employees",
        ]
        self.raw_responses = (
            RawResponse.objects.filter(
                path__slug__in=slugs,
                client=self.request.user.client,
                location__in=self.locations.values_list("name", flat=True),
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .exclude(data=list())
            .only("data", "location")
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
            temp["percentage_of_all_employees_covered_by_the_system"] = round(
                (
                    int(entry[0]["coveredbythesystem"])
                    / total_number_of_employees_covered_by_the_system
                )
                * 100,
                2,
            )
            temp["percentage_of_internally_audited_workers"] = round(
                (
                    int(entry[0]["internallyaudited"])
                    / total_number_of_internally_audited_workers
                )
                * 100,
                2,
            )
            temp["percentage_of_all_employees_internally_audited"] = round(
                (
                    int(entry[1]["coveredbythesystem"])
                    / total_number_of_employees_covered_by_the_system
                )
                * 100,
                2,
            )
            temp["percentage_of_workers_who_are_not_emplyees_internally_audited"] = (
                round(
                    (
                        int(entry[1]["internallyaudited"])
                        / total_number_of_internally_audited_workers
                    )
                    * 100,
                    2,
                )
            )
            temp["percentage_of_all_employees_externally_audited"] = round(
                (
                    int(entry[2]["coveredbythesystem"])
                    / total_number_of_employees_covered_by_the_system
                )
                * 100,
                2,
            )
            temp["percentage_of_workers_who_are_not_emplyees_externally_audited"] = (
                round(
                    (
                        int(entry[2]["internallyaudited"])
                        / total_number_of_internally_audited_workers
                    )
                    * 100,
                    2,
                )
            )
            local_response_data.append(temp)
        return local_response_data

    def get_work_related_ill_health(self):
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
        number_of_hours_worked_responses = self.get_number_of_hours_worked()
        for entry in data:
            _ = number_of_hours_worked_responses.filter(
                year=entry["year"], month=entry["month"]
            ).first()
            if _ is not None:
                number_of_hours = self.process_number_of_hours(
                    number_of_hours_worked_responses.filter(
                        year=entry["year"], month=entry["month"]
                    )
                    .first()
                    .data
                )
            else:
                number_of_hours = 1000000

            entry["rate_of_fatalities_as_a_result_of_work_related_injury"] = (
                int(entry["fatalities"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
            entry[
                "rate_of_high_consequence_work_related_injuries_excluding_fatalities"
            ] = (
                int(entry["highconsequence"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
            entry["rate_of_recordable_work_related_injuries"] = (
                int(entry["recordable"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
        return data

    def process_number_of_hours(self, number_of_hours):
        if isinstance(number_of_hours, dict):
            pattern = re.compile(r"\d+")
            matches = pattern.findall(number_of_hours["Q1"])
            integer_value = int("".join(matches))
            return integer_value
        else:
            return number_of_hours

    def get_rate_of_injuries_who_are_workers_but_not_employees(self):
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
        number_of_hours_worked_responses = self.get_number_of_hours_worked()
        for entry in data:
            _ = number_of_hours_worked_responses.filter(
                year=entry["year"], month=entry["month"]
            ).first()
            if _ is not None:
                number_of_hours = self.process_number_of_hours(
                    number_of_hours_worked_responses.filter(
                        year=entry["year"], month=entry["month"]
                    )
                    .first()
                    .data
                )
            else:
                number_of_hours = 1000000
            entry["rate_of_fatalities_as_a_result_of_work_related_injury"] = (
                int(entry["fatalities"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
            entry[
                "rate_of_high_consequence_work_related_injuries_excluding_fatalities"
            ] = (
                int(entry["highconsequence"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
            entry["rate_of_recordable_work_related_injuries"] = (
                int(entry["recordable"]) / int(entry["numberofhoursworked"])
            ) * number_of_hours
        return data

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

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data["organisation"]
        self.location = serializer.validated_data.get("location")  # * This is optional
        # * Set Locations Queryset
        self.locations = set_locations_data(
            organisation=self.organisation,
            corporate=self.corporate,
            location=self.location,
        )
        self.set_raw_responses()
        formal_joint_management = self.get_formal_joint_management()
        response_data = dict()
        formal_joint_management = (formal_joint_management,)
        workers_covered_by_an_occupational_health_and_safety_management_system = (
            self.get_workers_covered_by_an_occupational_health_and_safety_management_system(),
        )
        rate_of_injuries_for_all_employees = (self.get_work_related_ill_health(),)
        rate_of_injuries_for_not_included_in_company_employees = (
            self.get_rate_of_injuries_who_are_workers_but_not_employees(),
        )
        ill_health_for_all_employees_analysis = (
            self.get_ill_health_for_all_employees_analysis(),
        )
        ill_health_for_all_workers_who_are_not_employees_analysis = (
            self.get_ill_health_for_all_workers_who_are_not_employees_analysis(),
        )

        response_data=            {
                "formal_joint_management": formal_joint_management,
                "workers_covered_by_an_occupational_health_and_safety_management_system": self.get_workers_covered_by_an_occupational_health_and_safety_management_system(),
                "rate_of_injuries_for_all_employees": self.get_work_related_ill_health(),
                "rate_of_injuries_for_not_included_in_company_employees": self.get_rate_of_injuries_who_are_workers_but_not_employees(),
                "ill_health_for_all_employees_analysis": self.get_ill_health_for_all_employees_analysis(),
                "ill_health_for_all_workers_who_are_not_employees_analysis": self.get_ill_health_for_all_workers_who_are_not_employees_analysis(),
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
