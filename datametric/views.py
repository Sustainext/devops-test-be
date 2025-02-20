from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FieldGroup, Path, RawResponse, DataPoint, Location
from .serializers import (
    FieldGroupSerializer,
    UpdateResponseSerializer,
    RawResponseSerializer,
    FieldGroupGetSerializer,
    GetClimatiqComputedSerializer,
    UpdateFieldGroupSerializer,
)
from authentication.models import CustomUser, Client
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from logging import getLogger
from datametric.View.Training_EmpPerfCareerDvlpmnt import (
    extract_from_diversity_employee,
)
from datametric.View.EmissionOzone import get_prev_form_data
from common.utils.value_types import safe_divide
from decimal import Decimal
import traceback
import sys
from azurelogs.azure_log_uploader import AzureLogUploader
from azurelogs.time_utils import get_current_time_ist
from collections import OrderedDict
from deepdiff import DeepDiff
import time

uploader = AzureLogUploader()


#             # Upload logs only when there is a change
#

logger = getLogger("file")
climatiq_logger = getLogger("climatiq_logger")


def sanitize_ordered_dict(data):
    if isinstance(data, OrderedDict):
        # Convert OrderedDict to a regular dict
        return {k: sanitize_ordered_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Recursively sanitize each item in the list
        return [sanitize_ordered_dict(item) for item in data]
    else:
        # Return the data as is if it's neither an OrderedDict nor a list
        return data


def generate_text_pattern(data):
    result = []

    for entry in data:
        # Create a list of key-value pairs in the desired format
        pairs = [f"'{key}' > '{value}'" for key, value in entry.items()]
        # Join the pairs with " > "
        result.append(" > ".join(pairs))

    # Join all entry strings with a newline or any other separator if needed
    return "\n".join(result)


def getLogDetails(user, field_group, form_data, diff_string):
    # Collect > Environment > Emissions > GHG Emission > Organisation > Corporate entity > Location > Year > Month > Scope > Category > Sub-category > Activity > Quantity > Unit
    # path_prefix - from field_group
    part_one = "Undefined Audit Log Prefix"
    try:
        # part_one = field_group.meta_data["audit_log_prefix"]
        field_group_module = field_group.meta_data["module"]
        field_group_submodule = field_group.meta_data["sub_module"]
        field_group_name = field_group.name
        part_one = f"Collect > {field_group_module} > {field_group_submodule} > {field_group_name}"
    except Exception as e:
        # print(e)
        part_one = "Undefined Audit Log Prefix"

    organization = form_data.get("organisation", "")
    corporate = form_data.get("corporate", "")
    location = form_data.get("location", "")
    if not organization and not corporate and location:
        organization = location.corporateentity.organization.name
        corporate = location.corporateentity.name

    part_two = (
        f"{organization}"
        + (f" > {corporate}" if corporate else "")
        + (f" > {location}" if location else "")
        + (f" > {form_data['year']}" if form_data.get("year") else "")
        + (f" > {form_data['month']}" if form_data.get("month") else "")
    )

    result_log = f"{part_one} > {part_two} > {diff_string['description']}"
    return result_log


def compare_objects(obj1, obj2):
    """
    Compare two objects and return a string describing their differences.

    Args:
        obj1: First object (original data)
        obj2: Second object (new data)

    Returns:
        dict: A dictionary describing the status and differences found or error message
    """
    # print("reached 106")
    status_string = "Row Update"
    # print(obj1, " is obj1 ^^^^^")
    # print(obj2, " is obj2 ^^^^^")

    try:
        # Check if inputs are valid lists
        if not isinstance(obj1, list) or not isinstance(obj2, list):
            return {
                "status_string": status_string,
                "description": "Unidentified Update",
            }

        # Handle case where obj2 is empty
        if not obj2:
            if obj1:  # If obj1 has data and obj2 is empty, all rows are deleted
                return {
                    "status_string": "Row Delete",
                    "description": f"All {len(obj1)} rows are deleted",
                }
            else:  # Both obj1 and obj2 are empty
                return {
                    "status_string": status_string,
                    "description": "No data in both objects",
                }

        # Handle case where obj1 is empty or has lesser length
        if not obj1 or len(obj1) < len(obj2) or obj1 == [{}]:
            added_rows = len(obj2) - len(obj1) if obj1 else len(obj2)
            if obj1 == [{}]:
                added_rows = len(obj2)
            if added_rows == 1:
                return {
                    "status_string": "Row Create",
                    "description": "A new row is created",
                }
            else:
                return {
                    "status_string": "Row Create",
                    "description": f"{added_rows} new rows are created",
                }

        # Handle case where obj2 has lesser length than obj1
        if len(obj2) < len(obj1):
            deleted_rows = len(obj1) - len(obj2)
            if deleted_rows == 1:
                return {
                    "status_string": "Row Delete",
                    "description": "A row is deleted",
                }
            else:
                return {
                    "status_string": "Row Delete",
                    "description": f"{deleted_rows} rows are deleted",
                }

        # Compare the two lists using DeepDiff
        diff = DeepDiff(obj1, obj2, ignore_order=True)

        if not diff:
            return {
                "status_string": status_string,
                "description": "No difference with previous rows saved",
            }

        # Handle changes in existing rows
        changes = []
        for change in diff.get("values_changed", {}).values():
            old_value = change["old_value"]
            new_value = change["new_value"]
            changes.append(f"Value changed from '{old_value}' to '{new_value}'")

        # Prepare final response
        if changes:
            return {
                "status_string": status_string,
                "description": f"Row values are changed: {', '.join(changes)}",
            }

    except Exception as e:
        return {"status_string": "Error", "description": str(e)}


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        return Response("User created successfully", status=status.HTTP_200_OK)


class FieldGroupListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        validation_serializer = FieldGroupGetSerializer(data=request.query_params)
        validation_serializer.is_valid(raise_exception=True)
        path_slug = validation_serializer.validated_data.get("path_slug")
        year = validation_serializer.validated_data.get("year")
        month = validation_serializer.validated_data.get("month", None)

        """ New Requirements """
        organisation = validation_serializer.validated_data.get("organisation", None)
        corporate = validation_serializer.validated_data.get("corporate", None)

        locale = validation_serializer.validated_data.get("location", None)

        try:
            path = Path.objects.get(slug=path_slug)
        except Path.DoesNotExist:
            return Response(
                {"error": "Path not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            user_instance: CustomUser = self.request.user
            client_instance = user_instance.client
            field_groups = FieldGroup.objects.filter(path=path)
            serialized_field_groups = FieldGroupSerializer(field_groups, many=True)
            # TODO: Need to change the query to be based on the location id, at present it's on location name

            # Checking form data if any
            path_instance = path
            raw_responses = RawResponse.objects.filter(
                path=path_instance,
                client=client_instance,
                locale=locale,
                corporate=corporate,
                organization=organisation,
                year=year,
                month=month,
            )
            serialized_raw_responses = RawResponseSerializer(raw_responses, many=True)
            resp_data = {}
            resp_data["form"] = serialized_field_groups.data
            if (
                path_slug
                == "gri-social-performance_and_career-414-2b-number_of_suppliers"
            ):
                resp_data["form_data"] = extract_from_diversity_employee(
                    serialized_raw_responses,
                    path__slug="gri-social-diversity_of_board-405-1b-number_of_employee",
                    client_id=client_instance.id,
                    locale=locale,
                    corporate=corporate,
                    organization=organisation,
                    year=year,
                    month=month,
                )
            elif path_slug == "gri-environment-air-quality-emission-ods":
                resp_data["pre_form_data"] = get_prev_form_data(locale, year)
            else:
                resp_data["form_data"] = serialized_raw_responses.data

            return Response(resp_data)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)


class CreateOrUpdateFieldGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        start_time = time.time()
        serializer = UpdateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        form_data = validated_data["form_data"]
        path = validated_data["path"]
        path_ins = Path.objects.get(slug=path)
        # Get the first FieldGroup associated with this Path
        field_group_name = "None"

        try:
            field_group = FieldGroup.objects.filter(path=path_ins).first()

            field_group_module = field_group.meta_data["module"]
            field_group_submodule = field_group.meta_data["sub_module"]
            field_group_name = f"{field_group_module}-{field_group_submodule}"
        except Exception as e:
            # print(e)
            field_group_name = "Missing Audit_log_prefix"
        # location = validated_data["location"]
        year = validated_data["year"]
        month = validated_data.get("month", None)

        """ New Requirements """
        organisation = validated_data.get("organisation", None)
        corporate = validated_data.get("corporate", None)
        locale = validated_data.get("location", None)
        # print(locale, " is the location")
        location_fetch = Location.objects.filter(name=locale).first()
        if location_fetch:
            corporate_fetch = location_fetch.corporateentity
            organisation_fetch = corporate_fetch.organization
        else:
            corporate_fetch = corporate
            organisation_fetch = organisation
        # print(location_fetch)
        user_instance: CustomUser = self.request.user
        client_instance = user_instance.client

        # if locale:
        try:
            # if locale:
            #     location = Location.objects.filter(id=locale.id).values_list("name")[0][
            #         0
            #     ]
            # else:
            #     location = None
            # Retrieve instances of related models
            path_instance = Path.objects.get(slug=path)

            # Try to get an existing RawResponse instance
            raw_response, created = RawResponse.objects.get_or_create(
                path=path_instance,
                client=client_instance,
                locale=locale,
                corporate=corporate,
                organization=organisation,
                year=year,
                month=month,
                defaults={
                    "data": form_data,
                    "user": user_instance,
                },
            )
            if created or raw_response is None:
                # print("A new RawResponse was created.")
                sanitized_result = sanitize_ordered_dict(raw_response.data)
                diff_string = compare_objects([{}], form_data)
            else:
                # print("The RawResponse already existed.")
                sanitized_result = sanitize_ordered_dict(raw_response.data)
                diff_string = compare_objects(sanitized_result, form_data)
            # Sanitize the data

            # print(diff_string,' is the diffstring')
            # print(form_data, ' is form data')
            action_type = "Row create"
            if not created:
                # If the RawResponse already exists, update its data
                raw_response.data = form_data
                # ? Should we also update the user field on who has latest updated the data?
                raw_response.save()
                action_type = "Row Update"

            logger.info("status check")
            logger.info(f"RawResponse: {raw_response}")
            logger.info(f"created: {created}")
            time_now = get_current_time_ist()
            role = user_instance.custom_role
            # first_item = form_data[0]  # Get the first dictionary
            # print(diff_string)
            event_details = diff_string["status_string"]
            field_group_obj = FieldGroup.objects.filter(path=path_ins).first()
            log_text = getLogDetails(
                user_instance, field_group_obj, validated_data, diff_string
            )
            orgnz = user_instance.orgs.first().name
            climatiq_logger.info(
                f"Time taken to create or update: {time.time() - start_time}"
            )
            log_start = time.time()
            log_data = [
                {
                    "EventType": "Collect",
                    "TimeGenerated": time_now,
                    "EventDetails": field_group_name,
                    "Action": event_details,
                    "Status": "Success",
                    "UserEmail": user_instance.email,
                    "UserRole": user_instance.custom_role.name,
                    "Logs": log_text,
                    "Organization": organisation_fetch.name,
                    "IPAddress": "192.168.1.1",
                },
            ]
            # orgs = user_instance.orgs
            uploader.upload_logs(log_data)
            climatiq_logger.info(
                f"Time taken to upload logs: {time.time() - log_start}"
            )
            return Response(
                {"message": "Form data saved successfully."},
                status=status.HTTP_200_OK,
            )

        except (
            Path.DoesNotExist,
            CustomUser.DoesNotExist,
            Client.DoesNotExist,
        ) as e:
            logger.info(f"Lookup error: {e}")
            return Response(
                {"message": "Path, User, or Client does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            filename = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
            stack_trace = traceback.format_exc()

            # Log detailed information about the error
            logger.error(
                f"An unexpected error occurred in {filename} at line {line_number}: {e}",
                exc_info=True,
            )
            logger.debug(f"Exception type: {exc_type.__name__}")
            logger.debug(f"Stack trace: {stack_trace}")

            # Return the error response with more context
            return Response(
                {
                    "message": "An unexpected error occurred.",
                    "error": str(e),
                    "file": filename,
                    "line": line_number,
                    "exception_type": exc_type.__name__,
                    "stack_trace": stack_trace,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetComputedClimatiqValue(APIView):
    """
    This API view is used to get the computed climatiq value for a given location, year, and month.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        validation_serializer = GetClimatiqComputedSerializer(data=request.query_params)
        validation_serializer.is_valid(raise_exception=True)
        # TODO: Need to change the query to be based on the location id, at present it's on location name
        location_obj = validation_serializer.validated_data.get("location")
        year = validation_serializer.validated_data.get("year")
        month = validation_serializer.validated_data.get("month")
        user_instance: CustomUser = self.request.user
        client_instance = user_instance.client
        path = Path.objects.filter(slug="gri-collect-emissions-scope-combined").first()
        datapoint = DataPoint.objects.filter(
            client_id=client_instance.id,
            month=month,
            year=year,
            locale=location_obj,
            path=path,
        ).select_related("raw_response")
        resp_data = {"result": []}
        for datapoints in datapoint:
            values = datapoints.json_holder
            for value in values:
                value["updated_at"] = datapoints.raw_response.updated_at
                resp_data["result"].append(value)

        for data in resp_data["result"]:
            data["co2e"] = safe_divide(data["co2e"], 1000)
        resp_data["scope_wise_data"] = {"scope_1": 0, "scope_2": 0, "scope_3": 0}
        try:
            for emission_data in resp_data["result"]:
                resp_data["scope_wise_data"][emission_data.get("scope")] += Decimal(
                    emission_data.get("co2e", 0)
                )
            resp_data["total_emission"] = sum(resp_data["scope_wise_data"].values())
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            resp_data["scope_wise_data"] = {"scope_1": 0, "scope_2": 0, "scope_3": 0}
        return Response(resp_data, status=status.HTTP_200_OK)


class UpdateFieldGroupView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request):
        serializer = UpdateFieldGroupSerializer(data=request.data)
        if serializer.is_valid():
            path_name = serializer.validated_data["path_name"]
            field_group = FieldGroup.objects.filter(path__slug=path_name).first()

            if not field_group:
                return Response(
                    {"error": f"FieldGroup with path name {path_name} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if "schema" in serializer.validated_data:
                field_group.schema = serializer.validated_data["schema"]
            if "ui_schema" in serializer.validated_data:
                field_group.ui_schema = serializer.validated_data["ui_schema"]

            field_group.save()
            return Response(
                {"message": "FieldGroup updated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
