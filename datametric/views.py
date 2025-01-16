from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FieldGroup, Path, RawResponse, DataPoint
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
from common.utils.value_types import safe_divide
from decimal import Decimal
import traceback
import sys
from azurelogs.azure_log_uploader import AzureLogUploader
from azurelogs.time_utils import get_current_time_ist
from collections import OrderedDict

uploader = AzureLogUploader()


#             # Upload logs only when there is a change
#

logger = getLogger("file")


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


def compare_objects(obj1, obj2):
    """
    Compare two objects and return a string describing their differences.

    Args:
        obj1: First object (original data)
        obj2: Second object (new data)

    Returns:
        str: A description of the differences found or error message
    """
    try:
        # Check if inputs are valid lists
        if not isinstance(obj1, list) or not isinstance(obj2, list):
            return "Error: Both inputs must be lists"

        # Handle case where obj1 is empty or has lesser length
        if not obj1 or len(obj1) < len(obj2):
            added_rows = len(obj2) - len(obj1) if obj1 else len(obj2)
            if added_rows == 1:
                return "A new row is created"
            else:
                return f"{added_rows} new rows are created"

        # Handle case where obj2 has lesser length than obj1
        if len(obj2) < len(obj1):
            deleted_rows = len(obj1) - len(obj2)
            if deleted_rows == 1:
                return "A row is deleted"
            else:
                return f"{deleted_rows} rows are deleted"

        if not obj2:
            return "Error: Second object is empty"

        differences = []

        # Iterate through each entry
        for i, (entry1, entry2) in enumerate(zip(obj1, obj2)):
            try:
                # Compare each field in the dictionaries
                for key in entry1.keys():
                    value1 = str(entry1[key])
                    value2 = str(entry2[key])

                    if value1 != value2:
                        if key == "Quantity":
                            differences.append(
                                f"{key} changed from {value1} {entry1.get('Unit', '')} "
                                f"to {value2} {entry2.get('Unit', '')}"
                            )
                        else:
                            differences.append(
                                f"{key} changed from '{value1}' to '{value2}'"
                            )

            except KeyError as e:
                return f"Error: Missing key {str(e)} in objects at index {i}"
            except Exception as e:
                return f"Error: Invalid object structure at index {i}: {str(e)}"

        if not differences:
            return "No differences found between the objects."

        return "\n".join(differences)

    except Exception as e:
        return f"Error: {str(e)}"


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
            else:
                resp_data["form_data"] = serialized_raw_responses.data

            return Response(resp_data)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)


class CreateOrUpdateFieldGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UpdateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        form_data = validated_data["form_data"]
        path = validated_data["path"]
        # location = validated_data["location"]
        year = validated_data["year"]
        month = validated_data.get("month", None)

        """ New Requirements """
        organisation = validated_data.get("organisation", None)
        corporate = validated_data.get("corporate", None)
        locale = validated_data.get("location", None)
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
            # Sanitize the data
            sanitized_result = sanitize_ordered_dict(raw_response.data)
            diff_string = compare_objects(sanitized_result, form_data)
            print(diff_string)
            action_type = "Row create"
            # eventtype-collect, event_details - form_data[0.key]
            # Action - row created, status - Success, user email = , user role
            # User role, date time, IP Address
            # Logs - Collect -> Environment -> Emissions -> GHG Emissions -> Organization -> Corporate
            # -> Sub Category -> Activity -> Year -> Month -> Unit
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
            event_string = f"{path}\nNew Value: 0\nOld Value: 0\n"
            role = user_instance.custom_role
            print(role, " is the role name")
            first_item = form_data[0]  # Get the first dictionary
            event_details = list(first_item.keys())[0]
            print(organisation, " is organization")
            log_data = [
                {
                    "EventType": "Collect",
                    "TimeGenerated": time_now,
                    "EventDetails": event_details,
                    "Action": action_type,
                    "Status": "Success",
                    "UserEmail": user_instance.email,
                    "UserRole": user_instance.custom_role.name,
                    "Logs": diff_string,
                    "Organization": organisation,
                    "IPAddress": "192.168.1.1",
                },
            ]
            print(log_data)
            uploader.upload_logs(log_data)
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
        )
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
