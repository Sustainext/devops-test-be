from datametric.models import RawResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from collections import defaultdict


class GeneralEmployeeAnalyzeView(APIView):

    def get_data(self, year, client_id, filter_by,exclude_corporate = False):
        path_slugs = [
        "gri-general-workforce_employees-2-7-a-b-permanent_employee",
        "gri-general-workforce_employees-2-7-a-b-temporary_employee",
        "gri-general-workforce_employees-2-7-a-b-nonguaranteed_hours_employees",
        "gri-general-workforce_employees-2-7-a-b-full_time_employee",
        "gri-general-workforce_employees-2-7-a-b-part_time_employee",
    ]
        rw_data = RawResponse.objects.filter(
            path__slug__in=path_slugs,
            client_id=client_id,
            year=year,
            **filter_by
        )
        if exclude_corporate:
            rw_data = rw_data.filter(corporate__isnull=True)

        return rw_data
    
    def extract_employee_type(self, path_slug):
        if "permanent_employee" in path_slug:
            return "permanent_employee"
        elif "temporary_employee" in path_slug:
            return "temporary_employee"
        elif "nonguaranteed_hours_employees" in path_slug:
            return "nonguaranteed_hours_employees"
        elif "full_time_employee" in path_slug:
            return "full_time_employee"
        elif "part_time_employee" in path_slug:
            return "part_time_employee"
        else:
            return "unknown_employee"
    
    def get_general_employee_data(
        self,
        raw_response,
    ):
    
        employee_data = defaultdict(
            lambda: {
                "type_of_employee": "",
                "male": {"total": 0, "yearsold30": 0, "yearsold30to50": 0, "yearsold50": 0},
                "female": {"total": 0, "yearsold30": 0, "yearsold30to50": 0, "yearsold50": 0},
                "others": {"total": 0, "yearsold30": 0, "yearsold30to50": 0, "yearsold50": 0},
            }
        )
        for response in raw_response:
            employee_type = self.extract_employee_type(response.path.slug)
            for index, data in enumerate(response.data):
                total = int(data.get("total", 0))  if data.get("total", 0) else 0
                yearsold30 = int(data.get("yearsold30", 0))  if data.get("yearsold30", 0) else 0
                yearsold30to50 = int(data.get("yearsold30to50", 0)) if data.get("yearsold30to50", 0) else 0
                yearsold50 = int(data.get("yearsold50", 0))  if data.get("yearsold50", 0) else 0
                
                if index == 0:  # Male
                    employee_data[employee_type]["male"]["total"] += total
                    employee_data[employee_type]["male"]["yearsold30"] += yearsold30
                    employee_data[employee_type]["male"]["yearsold30to50"] += yearsold30to50
                    employee_data[employee_type]["male"]["yearsold50"] += yearsold50
                elif index == 1:  # Female
                    employee_data[employee_type]["female"]["total"] += total
                    employee_data[employee_type]["female"]["yearsold30"] += yearsold30
                    employee_data[employee_type]["female"]["yearsold30to50"] += yearsold30to50
                    employee_data[employee_type]["female"]["yearsold50"] += yearsold50
                elif index == 2:  # Others
                    employee_data[employee_type]["others"]["total"] += total
                    employee_data[employee_type]["others"]["yearsold30"] += yearsold30
                    employee_data[employee_type]["others"]["yearsold30to50"] += yearsold30to50
                    employee_data[employee_type]["others"]["yearsold50"] += yearsold50

            employee_data[employee_type]["type_of_employee"] = employee_type
            
        return [data for data in employee_data.values()]

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data.get("organisation")
        corporate = serializer.validated_data.get("corporate")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        client_id = self.request.user.client.id

        if self.start.year == self.end.year:
            year = self.start.year
        else:
            return Response(
                {"error": "Start and End year should be same."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rawres = {}
        filter_by = {}
        exclude_corporate = False

        if corporate:
            filter_by['corporate'] = corporate
        elif organisation:
            filter_by['organization'] = organisation
            exclude_corporate = True

        if filter_by:
            rw_data = self.get_data(year, client_id, filter_by,exclude_corporate)
            rawres = self.get_general_employee_data(rw_data)

        final = {
            "total_number_of_employees": rawres
        }
        return Response(final, status=status.HTTP_200_OK)