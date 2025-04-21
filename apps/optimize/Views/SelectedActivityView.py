from apps.optimize.models.SelectedAvtivityModel import SelectedActivity
from apps.optimize.Serializers.SelectedActivitySerializer import (
    SelectedActivitySerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.optimize.models.OptimizeScenario import Scenerio
from django.shortcuts import get_object_or_404


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

    def delete(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of objects with 'id' for deletion."},
                status=400,
            )

        ids_to_delete = [item.get("id") for item in data if item.get("id") is not None]

        if not ids_to_delete:
            return Response(
                {"detail": "No valid 'id' found in request data."}, status=400
            )

        # Delete only those that belong to this scenario
        deleted_count, _ = SelectedActivity.objects.filter(
            id__in=ids_to_delete, scenario=scenario
        ).delete()

        return Response({"deleted": deleted_count}, status=204)
