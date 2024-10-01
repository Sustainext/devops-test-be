from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from sustainapp.Serializers.TaskdashboardRetriveSerializer import (
    ClientTaskDashboardSerializer,
)
from django.utils import timezone


# get assigned by task
class AssignedEmissionTask(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            ClientTaskDashboard.objects.filter(assigned_by=self.request.user)
            .exclude(
                roles__in=[3, 4]
            )  # Confirm with the team -> 3 completed, 4 -> the task is calculated
            .filter(task_status__in=[0, 4])
        )

        # STATUS_CHOICES
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

        filters = {
            "location": self.request.query_params.get("location"),
            "year": self.request.query_params.get("year"),
            "month": self.request.query_params.get("month"),
        }

        return queryset.filter(**{k: v for k, v in filters.items() if v})

    def prepare_data(self, data):
        response_data = {str(i): [] for i in range(1, 4)}
        for task in data:
            scope = str(task["scope"])
            response_data[scope].append(
                {
                    "id": task["id"],
                    "task_rowdatabatch": [],
                    "subCategory": task["subcategory"],
                    "category": task["category"],
                    "modifiedTime": None,
                    "unit": [task["unit1"], task["unit2"] or ""],
                    "unitType": "",
                    "fileName": task["filename"] or "no filename found",
                    "assignTo": task["assign_to_email"],
                    "scope": int(task["scope"]),
                    "sector": task["category"],
                    "value1": (
                        float(task["value1"]) if task["value1"] is not None else None
                    ),
                    "unit_type": None,
                    "unit1": task["unit1"],
                    "value2": (
                        float(task["value2"]) if task["value2"] is not None else None
                    ),
                    "unit2": task["unit2"] or "",
                    "file": task["file"],
                    "filename": task["filename"] or "no filename found",
                    "assign_to": task["assign_to_email"],
                    "file_modified_at": task["file_modified_at"],
                    "emmissionfactorid": task["factor_id"],
                    "year": str(task["year"]),
                    "region": task["region"],
                    "source_lca_activity": None,
                    "data_quality_flags": [],
                    "constituent_gases": {
                        "ch4": 0.0,
                        "co2": 0.0,
                        "n2o": 0.0,
                        "co2e_other": None,
                        "co2e_total": 0.0,
                    },
                    "audit_trail": None,
                    "activity_data": {
                        "activity_unit": None,
                        "activity_value": 0.0,
                    },
                    "batch": 0,
                    "uploadedBy": "",
                    "selectedActivity": task["activity"],
                    "activities": "",
                    "activity_name": task["activity"],
                }
            )
        response_data.update(
            {
                "location": data[0]["location"] if data else "",
                "year": data[0]["year"] if data else "",
                "month": data[0]["month"] if data else "",
            }
        )
        return response_data

    def get(self, request, format=None):
        queryset = self.get_queryset()

        serializer = ClientTaskDashboardSerializer(queryset, many=True)
        response_data = self.prepare_data(serializer.data)

        return Response(data=response_data, status=HTTP_200_OK)
