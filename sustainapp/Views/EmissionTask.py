from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard, User_client, RowDataBatch
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_200_OK
from sustainapp.Serializers.TaskdashboardRetriveSerializer import (
    ClientTaskDashboardSerializer,
)


# Get approved task
class EmissionTask(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            ClientTaskDashboard.objects.filter(assigned_to=self.request.user)
            .exclude(roles__in=[3, 4])
            .filter(task_status__in=[1, 3])
        )

        # STATUS_CHOICES =
        #     (0, "in_progress"),
        #     (1, "approved"),
        #     (2, "under_review"),
        #     (3, "completed"),
        #     (4, "reject"),

        # ROLES
        # 1 = emission self assigned task
        # 2 = emission assigned-by someone else ( NOT CONFIRM )
        # 3 = task created from my task
        # 4 = emission task calculated
        location = self.request.query_params.get("location")
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        if location:
            queryset = queryset.filter(location=location)
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset()
        serializer = ClientTaskDashboardSerializer(queryset, many=True)
        response_data = {"1": [], "2": [], "3": []}
        for task in serializer.data:
            response_data[str(task["scope"])].append(
                {
                    "id": task["id"],
                    "task_rowdatabatch": [],
                    "subCategory": task["subcategory"],
                    "category": task["category"],
                    "modifiedTime": None,
                    "unit": [task["unit1"], task["unit2"] if task["unit2"] else ""],
                    "unitType": "",
                    "fileName": (
                        "no filename found"
                        if not task["filename"]
                        else task["filename"]
                    ),
                    "assignTo": task["assign_to_email"],
                    "scope": int(task["scope"]),
                    "sector": task["category"],
                    "value1": None if task["value1"] is None else float(task["value1"]),
                    "unit_type": None,
                    "unit1": task["unit1"],
                    "value2": None if task["value2"] is None else float(task["value2"]),
                    "unit2": task["unit2"] if task["unit2"] else "",
                    "file": task["file"],
                    "filename": (
                        "no filename found"
                        if not task["filename"]
                        else task["filename"]
                    ),
                    "assign_to": task["assign_to_email"],
                    "file_modified_at": task["file_modified_at"],
                    "emmissionfactorid": task["factor_id"],
                    "year": str(task["year"]),
                    "region": task["region"],  # Example, modify as needed
                    "source_lca_activity": None,
                    "data_quality_flags": [],
                    "constituent_gases": {
                        "ch4": 0.0,
                        "co2": 0.0,  # Example conversion; adjust as needed
                        "n2o": 0.0,
                        "co2e_other": None,
                        "co2e_total": 0.0,  # Example conversion; adjust as needed
                    },
                    "audit_trail": None,
                    "activity_data": {
                        "activity_unit": None,
                        "activity_value": 0.0,  # Example conversion; adjust as needed
                    },
                    "batch": 0,
                    "uploadedBy": "",
                    "selectedActivity": task["activity"],
                    "activities": "",
                    "activity_name": task["activity"],
                }
            )
            response_data["location"] = task["location"]
            response_data["year"] = task["year"]
            response_data["month"] = task["month"]
        return Response(response_data, status=HTTP_200_OK)
