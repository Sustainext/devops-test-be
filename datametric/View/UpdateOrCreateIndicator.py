from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from datametric.models import Path, FieldGroup
from datametric.serializers import UpdateFieldGroupSerializer
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError


class UpdateOrCreateIndicatorView(APIView):
    """
    A PUT API that updates or creates path, schema and ui_schema
    removing dependency from frontend.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateFieldGroupSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        path_name = serializer.validated_data["path_name"]
        schema = serializer.validated_data.get("schema")
        ui_schema = serializer.validated_data.get("ui_schema")
        is_new = serializer.validated_data["is_new"]

        if is_new:
            try:
                # * Create a new path object
                path_object = Path.objects.create(
                    name=path_name, slug=slugify(path_name)
                )
                path_object.save()
            except IntegrityError:
                raise ValidationError(
                    f"Bro, this path name slug {slugify(path_name)} already exists"
                )
        else:
            try:
                path_object = Path.objects.get(slug=path_name)
            except ObjectDoesNotExist:
                raise ValidationError(
                    "Bro, path name doesn't exist, turn is_new to True if creating new."
                )

        # * Check field group exists
        try:
            field_group_object = FieldGroup.objects.get(path=path_object)
            # * We have to update the field group object
            if ui_schema:
                field_group_object.ui_schema = ui_schema
            if schema:
                field_group_object.schema = schema
            field_group_object.save()
            return Response(
                data={
                    "message": f"Field Group {'schema' if schema else 'ui_schema'} Updated",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        except ObjectDoesNotExist:
            # * Create a new field_group object
            # * Check both schema and UI Schema given or not.
            if not (ui_schema and schema):
                raise ValidationError(
                    "You didn't pass both schema and UI Schema and you want to create a new indicator, how is that possible bhai/behan?"
                )

            field_group_object = FieldGroup.objects.create(
                path=path_object, meta_data={}, ui_schema=ui_schema, schema=schema
            )
            field_group_object.save()
            return Response(
                data={
                    "message": "New Indicator Created",
                    "data": {
                        "path_slug": path_object.slug,
                        "field_group": {
                            "schema": field_group_object.schema,
                            "ui_schema": field_group_object.ui_schema,
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )
