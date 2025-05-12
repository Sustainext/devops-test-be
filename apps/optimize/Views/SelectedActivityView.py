from apps.optimize.models.SelectedActivityModel import SelectedActivity
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
        """
        Handles POST requests to update selected activities for a given scenario.

        This method performs selective create and delete operations based on the difference
        between the incoming payload and the existing data in the database for the specified scenario.

        Validations and logic:
        1. If there are no existing selected activities in the database for the scenario,
        all items in the payload are directly created.

        2. If selected activities already exist for the scenario:
        - Each incoming activity is checked against existing ones.
        - If an activity in the payload is not in the database, it is created.
        - If an activity is already present, it is left unchanged (no duplicate or update).
        - This avoids unnecessary database writes.

        3. If an activity exists in the database but is not included in the incoming payload,
        that activity is considered deselected and is deleted from the database.

        Returns:
            201 Created — with the list of all currently selected activities (existing and newly added).
            400 Bad Request — if the input data is not a list or fails validation.
        """
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
            incoming_uuids = {item["uuid"] for item in serializer.validated_data}

            with transaction.atomic():
                # Get existing records
                existing_qs = SelectedActivity.objects.filter(scenario=scenario)
                existing_map = {obj.uuid: obj for obj in existing_qs}
                existing_uuids = set(existing_map.keys())

                # Find differences
                to_delete_ids = existing_uuids - incoming_uuids
                to_create_data = [
                    item
                    for item in serializer.validated_data
                    if item["uuid"] not in existing_uuids
                ]

                # Delete only removed activities
                if to_delete_ids:
                    SelectedActivity.objects.filter(
                        scenario=scenario, uuid__in=to_delete_ids
                    ).delete()

                # Create new ones
                activity_objects = [
                    SelectedActivity(**{**item, "scenario": scenario})
                    for item in to_create_data
                ]
                SelectedActivity.objects.bulk_create(activity_objects)

            # Return all currently selected activities (existing + new)
            current_selected = SelectedActivity.objects.filter(scenario=scenario)
            response_serializer = SelectedActivitySerializer(
                current_selected, many=True
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
