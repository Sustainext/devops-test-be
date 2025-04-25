from apps.optimize.models.SelectedAvtivityModel import SelectedActivity
from apps.optimize.Serializers.SelectedActivitySerializer import (
    SelectedActivitySerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.optimize.models.OptimizeScenario import Scenerio
from django.shortcuts import get_object_or_404
from django.db import transaction


class SelectedActivityView(APIView):
    """This class defines the view for the SelectedActivity model.
    It uses the SelectedActivitySerializer for serialization and deserialization.
    It allows retrieving and creating selected activities for a given scenario.
    It also allows deleting selected activities for a given scenario.
    """

    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        selected_activities = SelectedActivity.objects.filter(scenario=scenario)
        serializer = SelectedActivitySerializer(selected_activities, many=True)
        return Response(serializer.data)

    def post(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)

        data = request.data

        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of activity objects."}, status=400
            )

        # Inject scenario ID into each dict for validation
        for item in data:
            item["scenario"] = scenario.id

        serializer = SelectedActivitySerializer(data=data, many=True)
        if serializer.is_valid():
            with transaction.atomic():
                SelectedActivity.objects.filter(scenario=scenario).delete()
                # Inject actual scenario instance before model instantiation
                activity_objects = [
                    SelectedActivity(**{**item, "scenario": scenario})
                    for item in serializer.validated_data
                ]
                SelectedActivity.objects.bulk_create(activity_objects)

            response_serializer = SelectedActivitySerializer(
                activity_objects, many=True
            )
            return Response(response_serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def patch(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        selected_activity = get_object_or_404(
            SelectedActivity, id=request.data.get("id"), scenario=scenario
        )
        serializer = SelectedActivitySerializer(
            selected_activity, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
