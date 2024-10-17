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
            .filter(task_status__in=["in_progress", "reject"])
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

        return queryset.filter(**filters)

    def prepare_data(self, data):
        response_data = {str(i): [] for i in range(1, 4)}
        for task in data:
            scope = str(task["scope"])
            response_data[scope].append(
                {
                    "id": task["id"],
                    "Emission": {
                        "Category": task["category"],
                        "Subcategory": task["subcategory"],
                        "Activity": task["activity"],
                        "activity_id": "",
                        "unit_type": None,
                        "Unit": task["unit1"],
                        "Quantity": (
                            float(task["value1"])
                            if task["value1"] is not None
                            else None
                        ),
                        "Unit2": task["unit2"],
                        "Quantity2": (
                            float(task["value2"])
                            if task["value2"] is not None
                            else None
                        ),
                        "file": {
                            "name": "",
                            "url": "",
                            "type": "",
                            "size": None,
                            "uploadDateTime": "",
                        },
                    },
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
