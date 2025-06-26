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
        Handles POST requests to update selected activities for a given scenario,
        synchronizing the database records to exactly match the incoming payload (by all fields).
        """
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of activity objects."}, status=400
            )

        for item in data:
            item["scenario"] = scenario.id

        serializer = SelectedActivitySerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated = serializer.validated_data

        # Index incoming data by uuid
        payload_by_uuid = {item["uuid"]: item for item in validated}
        incoming_uuids = set(payload_by_uuid.keys())

        with transaction.atomic():
            # Query existing activities, index by uuid
            existing_qs = SelectedActivity.objects.filter(scenario=scenario)
            existing_by_uuid = {obj.uuid: obj for obj in existing_qs}
            existing_uuids = set(existing_by_uuid.keys())

            # DELETE: For DB items not in payload, delete
            to_delete_uuids = existing_uuids - incoming_uuids
            if to_delete_uuids:
                SelectedActivity.objects.filter(
                    scenario=scenario, uuid__in=to_delete_uuids
                ).delete()

            # CREATE & UPDATE
            create_objs = []
            update_objs = []
            for uuid, item in payload_by_uuid.items():
                if uuid in existing_by_uuid:
                    obj = existing_by_uuid[uuid]
                    updated = False
                    # Compare all serializable fields (except id, scenario, uuid)
                    for field in item:
                        if field in ["id", "scenario", "uuid"]:
                            continue
                        if getattr(obj, field) != item[field]:
                            setattr(obj, field, item[field])
                            updated = True
                    if updated:
                        update_objs.append(obj)
                    # else, nothing to do (identical)
                else:
                    # create new row
                    create_objs.append(
                        SelectedActivity(**{**item, "scenario": scenario})
                    )

            # BULK UPDATE CHANGED ROWS
            if update_objs:
                SelectedActivity.objects.bulk_update(
                    update_objs,
                    [f for f in item if f not in ["id", "scenario", "uuid"]],
                )
            # BULK CREATE NEW ROWS
            if create_objs:
                SelectedActivity.objects.bulk_create(create_objs)

        # Return all current activities
        current_selected = SelectedActivity.objects.filter(scenario=scenario)
        response_serializer = SelectedActivitySerializer(current_selected, many=True)
        return Response(response_serializer.data, status=201)

    def patch(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        data_list = request.data

        if not isinstance(data_list, list):
            return Response({"detail": "Expected a list of updates."}, status=400)

        updated_activities = []
        errors = []
        no_changes = []

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

            # Check if there are actual changes by comparing with current data
            current_data = SelectedActivitySerializer(selected_activity).data
            has_changes = False

            # Compare each field in the update with current data
            for key, value in item.items():
                if key != "id" and key in current_data and current_data[key] != value:
                    has_changes = True
                    break

            if not has_changes:
                # No changes detected, skip saving
                no_changes.append({"id": activity_id, "detail": "No changes detected"})
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
        if no_changes:
            response_data["no_changes"] = no_changes
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=200 if not errors else 207)
