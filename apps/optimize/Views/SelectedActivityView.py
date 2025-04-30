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
        data_list = request.data

        if not isinstance(data_list, list):
            return Response({"detail": "Expected a list of updates."}, status=400)

        updated_activities = []
        errors = []

        for item in data_list:
            activity_id = item.get("id")
            if not activity_id:
                errors.append({"detail": "Missing 'id' in one of the items."})
                continue

            try:
                selected_activity = SelectedActivity.objects.get(
                    id=activity_id, scenario=scenario
                )
            except SelectedActivity.DoesNotExist:
                errors.append(
                    {"id": activity_id, "detail": "SelectedActivity not found."}
                )
                continue

            serializer = SelectedActivitySerializer(
                selected_activity, data=item, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                updated_activities.append(serializer.data)
            else:
                errors.append({"id": activity_id, "errors": serializer.errors})

        response_data = {"updated": updated_activities}
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=200 if not errors else 207)
