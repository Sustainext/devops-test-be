from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard, Location
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
            ClientTaskDashboard.objects.all()
            .exclude(roles__in=[3, 4])
            .filter(task_status__in=["approved", "completed"])
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
        filter_by = {
            "location_id": self.request.query_params.get("location"),
            "year": self.request.query_params.get("year"),
            "month": self.request.query_params.get("month"),
        }

        return queryset.filter(**filter_by)

    def get(self, request, format=None):
        try:
            queryset = self.get_queryset()
            serializer = ClientTaskDashboardSerializer(queryset, many=True)
            response_data = {"1": [], "2": [], "3": []}
            for task in serializer.data:
                response_data[str(task["scope"])].append(
                    {
                        "id": task["id"],
                        "Emission": {
                            "assigned_to": task["assigned_to"],
                            "Category": task["category"],
                            "Subcategory": task["subcategory"],
                            "Activity": task["activity"],
                            "activity_id": task["activity_id"],
                            "unit_type": "",
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
                            "file": (
                                {
                                    "name": "",
                                    "url": "",
                                    "type": "",
                                    "size": None,
                                    "uploadDateTime": "",
                                }
                                if not task["file_data"]
                                else task["file_data"]
                            ),
                        },
                    }
                )
                response_data["location"] = task["location"]
                response_data["location_name"] = (
                    Location.objects.get(
                        id=self.request.query_params.get("location")
                    ).name
                    if task["location"]
                    else ""
                )
                response_data["year"] = task["year"]
                response_data["month"] = task["month"]
            return Response(response_data, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400,
            )
