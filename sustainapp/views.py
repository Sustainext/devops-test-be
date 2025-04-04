from django.conf import settings
from django.db.models import F
from rest_framework import viewsets
from rest_framework import generics
from django.http import JsonResponse
from rest_framework.response import Response
from decimal import *
from django.contrib.auth.models import User
from authentication.models import CustomUser
from sustainapp.models import (
    Organization,
    Corporateentity,
    Location,
    Stakeholdergroup,
    Stakeholder,
    Task,
    Userorg,
    RowDataBatch,
    Batch,
    Framework,
    Mygoal,
    TaskDashboard,
    Client,
    User_client,
    Sdg,
    Rating,
    Certification,
    Target,
    Regulation,
)
from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import get_user_model
# User = get_user_model()

from django.core.exceptions import (
    ValidationError,
)

from datetime import date

from sustainapp.serializers import (
    OrganizationSerializer,
    LocationSerializer,
    StakeholdergroupSerializer,
    StakeholderSerializer,
    TaskSerializer,
    OrganizationOnlySerializer,
    CorporateentityOnlySerializer,
    ClientSerializer,
    BatchSerializer,
    MygoalSerializer,
    TaskDashboardSerializer,
    UserorgSerializer,
)

from rest_framework import status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework import serializers
from .utils import (
    check_same_client,
    handle_none,
    validation_org_input,
    client_request_data,
    client_request_data_modelviewset,
)
from django.db.models import Sum, Q
from django.db import transaction
# Email notification
# from django.core.mail import send_mail
# from django.conf import settings
# from django.template.loader import render_to_string

import logging
import copy

from authentication.models import LoginCounter

# canada bill s-211 Annual report started from here
# from .serializers import Screen1Serializer,Screen2Serializer,Screen3Serializer,Screen4Serializer,Screen5Serializer,Screen6Serializer,Screen7Serializer,Screen8Serializer
# from sustainapp.models import AnnualReport

# Create a logger
logger = logging.getLogger()

# Create a file handler for the warning log
warning_handler = logging.FileHandler("warning.log")

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
warning_handler.setFormatter(formatter)

# Set the level for the handler to the lowest level you want to capture
warning_handler.setLevel(
    logging.INFO
)  # Set the level to INFO to capture both info and warning messages

# Add the handler to the logger
logger.addHandler(warning_handler)

# Set the level of the root logger to the lowest level you want to capture
logger.setLevel(
    logging.INFO
)  # Set the level to INFO to capture both info and warning messages


def log_call_start():
    logger.info("-----------------Call started from here----------------")


user_log = logging.getLogger("user_logger")  # For general logs


class ClientViewset(viewsets.ModelViewSet):
    """Creating API's for client"""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        log_call_start()
        logging.info("ClientViewset: Processing request")
        queryset = self.get_queryset()
        client_data = self.get_serializer(queryset, many=True).data
        logging.info("ClientViewset: Returning response")
        return Response({"data": client_data}, status=status.HTTP_200_OK)

    def create(self, request):
        logging.info(f"Request data: {request.data}")

        _serializer = self.serializer_class(data=self.request.data)
        if _serializer.is_valid():
            _serializer.save()
            return Response(_serializer.data, status=status.HTTP_200_OK)
        return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        logging.info(f"Deleting organization instance - {instance}")
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    def update(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"])
    def client_details_by_username(self, request, username=None):
        # Find the user by username
        try:
            username = request.query_params.get("username")
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # Find the User_client relationship
        try:
            user_client = User_client.objects.get(user=user)
        except User_client.DoesNotExist:
            return Response(
                {"error": "Client for this user not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Retrieve the associated client
        client = user_client.client
        # Serialize the client data
        serializer = ClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def users_of_client(self, request, pk=None):
        """This method returns all users associated with a specific client."""
        try:
            # Ensure the client exists
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Filter User_client instances by the client
        try:
            user_clients = self.queryset.filter(client=client)

        except Exception as e:
            return Response(
                {"error": "Client have no users"}, status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the data
        serializer = self.get_serializer(user_clients, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        logging.info(f"Deleting organization instance - {instance}")
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def UserOrgDetails(request):
    try:
        username = request.user.username

        user = CustomUser.objects.get(username=username)
        user_login_counter = LoginCounter.objects.get(user=user)
        is_first_login = 1 if user_login_counter.needs_password_change == True else 0
    except Exception as e:
        return Response(
            {"error": "missing Details"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_detail = list(
            CustomUser.objects.filter(client_id=request.client.id, username=username)
            .annotate(client_name=F("client__name"))
            .values(
                "id",
                "username",
                "email",
                "client_id",
                "client_name",
                "is_superuser",
                "first_name",
                "last_name",
                "email",
                "is_staff",
                "is_active",
                "date_joined",
            )
        )

        if user_detail == []:
            raise ValidationError("User does not exist")
        user_org_queryset = Userorg.objects.filter(user=user_detail[0]["id"])
        user_orgwise = list(
            user_org_queryset.values(
                "id",
                "organization",
                "group",
                "department",
                "designation",
                "profile_picture",
            )
        )
        user_organisations = user_org_queryset.values_list("organization", flat=True)
        if user_orgwise == []:
            raise ValidationError("User is not mapped with any organisation")
        # TODO: Show all details of all the organisations mapped to the user
        org_data = list(
            Organization.objects.filter(client_id=request.client)
            .filter(id__in=user_organisations)
            .values(
                "id",
                "name",
                "type_corporate_entity",
                "owner",
                "location_of_headquarters",
                "sector",
                "currency",
            )
        )
        if org_data == []:
            raise ValidationError("Organisation does not exist")

        return Response(
            {
                "user_detail": user_detail,
                "user_orgwise": user_orgwise,
                "org_data": org_data,
                "has_login_first": is_first_login,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logging.error("Error in UserOrgDetails view: %s", e, exc_info=True)
        return Response(
            {"message": str(e), "error": "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class StructureList(generics.ListAPIView):
    """API for getting Organization structure"""

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization = user.orgs.all().prefetch_related("corporatenetityorg")
        return organization

    def list(self, request):
        queryset = self.get_queryset()
        serializer = OrganizationSerializer(
            queryset, many=True, context={"request": self.request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationViewset(viewsets.ModelViewSet):
    """Endpoints for Organizations"""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        check_same_client(request.client, instance)
        logging.info(f"Deleting organization instance - {instance}")
        user_log.info(
            f"Organisation: ({instance.name}), ID: ({instance.id}) deleted by user {request.user.username}"
        )
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.datapoint_set.all().delete()
        return super().perform_destroy(instance)

    def update(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        check_same_client(request.client, instance)
        request_data = request.data.copy()

        request_data = client_request_data_modelviewset(request_data, request.client)
        serializer = self.get_serializer(
            instance, data=request_data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()


class CreateOrganization(generics.CreateAPIView):
    """Create Organization"""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            organization = serializer.save(client=self.request.user.client)

            # Link the organization to the user using the ManyToMany field on the user model.
            self.request.user.orgs.add(organization)

            # Link the organization with the Userorg instance.
            user_org, created = Userorg.objects.get_or_create(user=self.request.user)
            user_org.organization.add(organization)
            user_org.save()

class CorporateViewset(viewsets.ModelViewSet):
    """Endpoints for Corporate"""

    queryset = Corporateentity.objects.all()
    serializer_class = CorporateentityOnlySerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        check_same_client(request.client, instance)
        logging.info(f"Deleting corporate instance - {instance}")
        user_log.info(
            f"Corporate ({instance.name}),ID: {instance.id} deleted by user {request.user.username}"
        )
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.datapoint_set.all().delete()
        return super().perform_destroy(instance)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        check_same_client(request.client, instance)
        data = client_request_data_modelviewset(request.data, request.client)

        serializer = self.get_serializer(
            instance, data=data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def list(self, request):
        organization_id = request.query_params.get("organization_id")
        if organization_id:
            corporate_entities = request.user.corps.filter(
                organization_id=organization_id
            )
            if corporate_entities.exists():
                serializer = CorporateentityOnlySerializer(
                    corporate_entities, many=True
                )
                return Response(serializer.data)
            else:
                return Response(
                    "No entities found for the provided organization ID.",
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                "Organization ID not provided.", status=status.HTTP_400_BAD_REQUEST
            )


class CreateCorporate(generics.CreateAPIView):
    """Create Corporate"""

    queryset = Corporateentity.objects.all()
    serializer_class = CorporateentityOnlySerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            corporate = serializer.save(client=self.request.user.client)

            # Link the corporate to the user using the ManyToMany field on the user model.
            self.request.user.corps.add(corporate)


class LocationViewset(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        check_same_client(request.client, instance)
        data = client_request_data_modelviewset(request.data, request.client)
        serializer = self.get_serializer(
            instance, data=data, partial=kwargs.get("partial", False)
        )

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        log_call_start()
        instance = self.get_object()
        check_same_client(request.client, instance)
        logging.info(f"deleting location instance:, {instance}")

        user_log.info(
            f"User {request.user} deleted location {instance.name} from {instance.client.name}"
        )
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.datapoint_set.all().delete()
        return super().perform_destroy(instance)


class CreateLocation(generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            location = serializer.save(client=self.request.user.client)

            self.request.user.locs.add(location)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def locationview(request):
    try:
        log_call_start()
        queryset = Location.objects.filter(client_id=request.client)
        location_data = LocationSerializer(queryset, many=True).data
        return Response(location_data, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"message": e.args})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def corporategetonly(request):
    try:
        log_call_start()
        corps = request.user.corps.all()
        corporate = Corporateentity.objects.filter(id__in=corps)
        corporate_data = CorporateentityOnlySerializer(corporate, many=True).data
        return Response(corporate_data)
    except Exception as e:
        return JsonResponse({"message": e.args})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def orggetonly(request):
    try:
        org = request.user.orgs.all()
        org_data = OrganizationOnlySerializer(org, many=True).data
        return Response(org_data)
    except Exception as e:
        return JsonResponse({"message": e.args})


def create_task(username, rows_created_now, scope_data):
    try:
        task = Task.objects.bulk_create(
            [
                Task(
                    name=entire_row["activity_data"]["activity_id"],
                    row_data_batch=RowDataBatch.objects.get(id=individual_row_data[0]),
                    assigned_to=User.objects.get(username=entire_row["assign_to"]),
                    assigned_by=User.objects.get(username=username),
                )
                for individual_row_data, entire_row in zip(rows_created_now, scope_data)
            ]
        )
        return task
    except Exception as e:
        return "Task creation failed"


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer = TaskSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Task.objects.filter(assigned_to=request.data["username"])
        serializer = TaskSerializer(queryset, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_org(request):
    try:
        log_call_start()
        data_filter = dict(request.query_params)
        user_id = list(
            User.objects.filter(username=data_filter["username"][0]).values("id")
        )[0]["id"]
        user_org = list(Userorg.objects.filter(user=user_id).values("organization"))[0][
            "organization"
        ]
        logging.info(f"get_org: User Organization - {user_org}")
        return Response(user_org, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"message": e.args})


def calculate_total(i):
    total_co2e = i.aggregate(total=Sum("co2e"))
    return total_co2e


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def AnalyseView(request):
    try:
        log_call_start()
        data_filter = dict(request.query_params)
        year = request.query_params.get("year")
        if year is None:
            return Response(
                {"message": "Missing required parameter: year"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # as of now no filtering with username
        username = request.query_params.get("username")
        if username is None:
            return Response(
                {"message": "Missing required parameter: username"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logging.info(
            f"AnalyseView: Query parameters - {data_filter}, username - {username}"
        )

        # Filerting corporates by client
        corporate_list = list(
            Corporateentity.objects.filter(client_id=request.client.id).values("name")
        )
        logging.info(f"AnalyseView: Corporate List - {corporate_list}")
        if corporate_list == []:
            return Response(
                {"message": "Corporate Data is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resp = {}
        # Looping for all Corporate
        for corporate in corporate_list:
            resp.update({corporate["name"]: {}})
            logging.info(f"AnalyseView: Processing Corporate - {corporate['name']}")

            # Filtering out emissions for the corporate in loop
            emission_org = RowDataBatch.objects.filter(
                batch__location__corporateentity__name=corporate["name"]
            )
            logging.info(
                f"AnalyseView: Emission Data before year filtering - {emission_org}"
            )

            emission_org = emission_org.filter(batch__year=data_filter["year"][0])
            logging.info(
                f"AnalyseView: Emission Data after year filtering - {emission_org}"
            )

            # total emissions value
            total_emission_value = emission_org.aggregate(total=Sum("co2e"))
            total_emission_value["total"] = handle_none(total_emission_value["total"])
            logging.info(f"AnalyseView: Total Emission Value - {total_emission_value}")

            # SCOPE DATA STARTS HERE
            logging.info("----------SCOPE DATA STARTS HERE-------")
            scope_list = [1, 2, 3]
            emission_data_scope = [emission_org.filter(scope=i) for i in scope_list]
            logging.info(f"emission_data_scope- {emission_data_scope}")
            scope_arr = []
            for i_scope, j_scope in zip(emission_data_scope, scope_list):
                if not i_scope:
                    logging.info(f"this iteration doesnt have data")
                else:
                    total_co2e_scope = calculate_total(i_scope)
                    total_co2e_scope["total"] = handle_none(total_co2e_scope["total"])
                    logging.info(f"{total_co2e_scope}")
                    logging.info(f"{type(total_emission_value['total'])}")
                    # Check if total_emission_value["total"] is very small or zero
                    try:
                        if total_emission_value["total"] is None or abs(
                            total_emission_value["total"] < Decimal("1E-50")
                        ):
                            contribution_scope = 0
                        else:
                            contribution_scope = (
                                total_co2e_scope["total"]
                                / total_emission_value["total"]
                                * 100
                            )
                    except ZeroDivisionError:
                        contribution_scope = 0
                    scope_arr.append(
                        {
                            "scope_name": "scope " + str(j_scope),
                            "total_co2e": round(total_co2e_scope["total"] / 1000, 2),
                            "contribution_scope": round(contribution_scope, 2),
                        }
                    )
                    logging.info("scope_arr {scope_arr}")
            resp[corporate["name"]]["scope"] = scope_arr
            logging.info(f"response {resp}")

            # Category data starts here
            logging.info("------CATEGORY STARTS HERE-----")
            category_list = list(RowDataBatch.objects.values("sector"))
            category_set = list(
                set([each_elem["sector"] for each_elem in category_list])
            )
            emission_data_category = []
            for i in category_set:
                em = emission_org.filter(sector=i)
                emission_data_category.append(em)
            logging.info(f"emission_data_category - {emission_data_category}")

            category_arr = []
            for i_category, j_category in zip(emission_data_category, category_set):
                if not i_category:
                    logging.info(f"this iteration doesnt have data")
                else:
                    total_co2e_category = calculate_total(i_category)
                    total_co2e_category["total"] = handle_none(
                        total_co2e_category["total"]
                    )
                    # Check if total_emission_value["total"] is very small or zero
                    if total_emission_value["total"] is None or abs(
                        total_emission_value["total"] < Decimal("1E-50")
                    ):
                        contribution_category = 0
                    else:
                        contribution_category = (
                            total_co2e_category["total"]
                            / total_emission_value["total"]
                            * 100
                        )
                    category_arr.append(
                        {
                            "source_name": j_category,
                            "total_co2e": round(total_co2e_category["total"] / 1000, 2),
                            "contribution_source": round(contribution_category, 2),
                        }
                    )

            resp[corporate["name"]]["source"] = category_arr
            logging.info(f"response {resp}")

            # Location data starts here
            logging.info("LOCATION STARTS HERE")
            location_list = list(
                Location.objects.filter(corporateentity__name=corporate["name"]).values(
                    "id", "name"
                )
            )
            logging.info(f"Location_list {location_list}")
            for i in location_list:
                i_id = i["id"]
            emission_data_location = [
                emission_org.filter(batch__location__id=i["id"]) for i in location_list
            ]

            location_arr = []
            for i, j in zip(emission_data_location, location_list):
                if not i:
                    logging.info(f"this iteration doesnt have data")
                else:
                    total_co2e_location = calculate_total(i)
                    total_co2e_location["total"] = handle_none(
                        total_co2e_location["total"]
                    )

                    # Check if total_emission_value["total"] is very small or zero
                    if total_emission_value["total"] is None or abs(
                        total_emission_value["total"] < Decimal("1E-50")
                    ):
                        contribution_location = 0
                    else:
                        contribution_location = (
                            total_co2e_location["total"]
                            / total_emission_value["total"]
                            * 100
                        )
                    location_arr.append(
                        {
                            "location_name": j["name"],
                            "total_co2e": round(total_co2e_location["total"] / 1000, 2),
                            "contribution_scope": round(contribution_location, 2),
                        }
                    )
            resp[corporate["name"]]["location"] = location_arr

            logging.info(f"response {resp}")

        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"AnalyseView: Error - {e}")
        return JsonResponse({"message": e.args}, status=status.HTTP_400_BAD_REQUEST)


class StakeholdergroupViewset(viewsets.ModelViewSet):
    # log_call_start()
    queryset = Stakeholdergroup.objects.all()
    serializer_class = StakeholdergroupSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        log_call_start()
        logging.info("Fetching Stakeholdergroup data")
        queryset = Stakeholdergroup.objects.all()

        stakeholdegroup_data = StakeholdergroupSerializer(queryset, many=True).data
        return Response(stakeholdegroup_data)
        # return Response(queryset)


class StakeholderViewset(viewsets.ModelViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Stakeholder.objects.all()
        stakeholder_data = StakeholderSerializer(queryset, many=True).data
        return Response(stakeholder_data)


class MygoalViewset(viewsets.ModelViewSet):
    # log_call_start()
    queryset = Mygoal.objects.all()
    serializer_class = MygoalSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        log_call_start()
        queryset = Mygoal.objects.filter(client_id=request.client.id)
        final_data = {"upcoming": "", "overdue": "", "completed": ""}
        today = date.today()
        logging.info(f"Today's date: {str(today)}")

        req_field_value = self.request.user.id

        final_data["completed"] = queryset.filter(
            completed=True, assigned_to=req_field_value
        )
        final_data["upcoming"] = queryset.filter(
            Q(completed=False, deadline__gte=today) & Q(assigned_to=req_field_value)
        )
        final_data["overdue"] = queryset.filter(
            Q(completed=False, deadline__lt=today) & Q(assigned_to=req_field_value)
        )
        serializerd_data_goal = {
            "upcoming": None,
            "overdue": None,
            "completed": None,
        }

        serializerd_data_goal["completed"] = (
            MygoalSerializer(final_data["completed"], many=True).data
            if final_data["completed"].exists()
            else [None]
        )
        serializerd_data_goal["upcoming"] = (
            MygoalSerializer(final_data["upcoming"], many=True).data
            if final_data["upcoming"].exists()
            else [None]
        )
        serializerd_data_goal["overdue"] = (
            MygoalSerializer(final_data["overdue"], many=True).data
            if final_data["overdue"].exists()
            else [None]
        )
        mygoal_data_union = serializerd_data_goal

        logging.info("Returning mygoal data union")
        return Response(mygoal_data_union, status=status.HTTP_200_OK)

    def create(self, request):
        logging.info(f"Request data: {request.data}")
        request_data = request.data.copy()
        request_data["client"] = request.client.id

        _serializer = self.serializer_class(data=request_data)
        if _serializer.is_valid():
            _serializer.save()
            return Response(_serializer.data, status=status.HTTP_200_OK)
        return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        check_same_client(request.client, instance)
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destory(self, instance):
        return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logging.info(f"Deleting instance: {instance}")
        check_same_client(request.client, instance)
        self.perform_destroy(instance)
        # instance.delete()
        return Response({"message": "Successfully Deleted"}, status=status.HTTP_200_OK)


class TaskDashboardViewset(viewsets.ModelViewSet):
    # log_call_start()
    queryset = TaskDashboard.objects.all()
    serializer_class = TaskDashboardSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        log_call_start()
        logging.info(f"Length of req.get: {len(request.GET)}")
        # DONT FORGET IMPLEMENT IMPLEMENT QUERYSET 2 FOR 'TASK' AND COMBINE IT FOR FILTERING
        queryset = TaskDashboard.objects.all().filter(client=request.client)
        final_data = {"upcoming": "", "overdue": "", "completed": ""}
        today = date.today()
        logging.info(f"Todays date: {str(today)}")

        req_field_value = self.request.user.id
        logging.error("KeyError: 'assigned_to' not found in request parameters")
        final_data["completed"] = queryset.filter(
            completed=True, assigned_to=req_field_value
        )
        final_data["upcoming"] = queryset.filter(
            Q(completed=False, deadline__gte=today) & Q(assigned_to=req_field_value)
        )
        final_data["overdue"] = queryset.filter(
            Q(completed=False, deadline__lt=today) & Q(assigned_to=req_field_value)
        )

        serializerd_data_task = {"upcoming": None, "overdue": None, "completed": None}

        serializerd_data_task["completed"] = (
            TaskDashboardSerializer(final_data["completed"], many=True).data
            if final_data["completed"].exists()
            else [None]
        )
        serializerd_data_task["upcoming"] = (
            TaskDashboardSerializer(final_data["upcoming"], many=True).data
            if final_data["upcoming"].exists()
            else [None]
        )
        serializerd_data_task["overdue"] = (
            TaskDashboardSerializer(final_data["overdue"], many=True).data
            if final_data["overdue"].exists()
            else [None]
        )

        task_data_union = serializerd_data_task
        logging.info(f"Task data union: {task_data_union}")
        return Response(task_data_union, status=status.HTTP_200_OK)

    def create(self, request):
        logging.info(f"Request data: {request.data}")
        request_data = request.data.copy()
        request_data["client"] = request.client.id

        _serializer = self.serializer_class(data=request_data)
        if _serializer.is_valid():
            _serializer.save()
            return Response(_serializer.data, status=status.HTTP_200_OK)
        return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        check_same_client(request.client, instance)
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destory(self, instance):
        return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logging.info(f"Deleting instance: {instance}")
        check_same_client(request.client, instance)
        self.perform_destroy(instance)
        return Response({"message": "Successfully Deleted"}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def UserOrgUpdateView(request):
    log_call_start()
    user_id = request.query_params.get("user_id")
    if not user_id:
        logger.error("User ID is required for UserOrgUpdateView")
        return Response(
            {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_obj = User.objects.get(id=user_id)
        userorg_obj = Userorg.objects.get(user=user_obj)
    except User.DoesNotExist:
        logger.error("User does not exist for User ID: %s", user_id)
        return Response(
            {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Userorg.DoesNotExist:
        logger.error("Userorg does not exist for User ID: %s", user_id)
        return Response(
            {"error": "Userorg does not exist for this user"},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = UserorgSerializer(userorg_obj, data=request.data, partial=True)
    if not serializer.is_valid():
        logger.error(
            "Invalid data received for UserOrgUpdateView: %s", serializer.errors
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    name = request.data.get("name")
    if name:
        first_name, *last_name = name.split(" ")
        last_name = " ".join(last_name)
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.save()
        serialized_data = serializer.data
        serialized_data["name"] = first_name + " " + last_name
        logger.info("UserOrg updated successfully for User ID: %s", user_id)
        return Response(serialized_data, status=status.HTTP_200_OK)
    else:
        logger.warning("Name not provided in the request for User ID: %s", user_id)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ColourViewset(viewsets.ModelViewSet):
    # log_call_start()
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    # add location and Year
    def list(self, request):
        log_call_start()

        location = request.query_params.get("location_id", "")
        year = request.query_params.get("year", "")
        # month = request.query_params['month']
        logger.info(
            "Received request for ColourViewset list with location: %s and year: %s",
            location,
            year,
        )
        try:
            location_obj = Location.objects.get(id=location)
            location_id = location_obj.id
            # check if user belongs to same client to which location belongs
            check_same_client(request.client, location_obj)
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            batch_data_query = Batch.objects.all().filter(
                location=location_id, year=year
            )
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            batch_data_ordered = BatchSerializer(batch_data_query, many=True).data
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            batch_data = [dict(bd) for bd in batch_data_ordered]
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            result = {
                "id": location_id,
                "location": location,
                "year": year,
                "months": {
                    "JAN": 0,
                    "FEB": 0,
                    "MAR": 0,
                    "APR": 0,
                    "MAY": 0,
                    "JUN": 0,
                    "JUL": 0,
                    "AUG": 0,
                    "SEP": 0,
                    "OCT": 0,
                    "NOV": 0,
                    "DEC": 0,
                },
            }
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            for each_data in batch_data:
                logger.info(
                    "Received request for ColourViewset list with location: %s and year: %s",
                    location,
                    year,
                )
                # FOR EVERY MONTH IN BATCH DB WE ARE RETURNING 1
                result["months"][each_data["month"]] = (
                    1  # SHOULD THIS BE CHANGED ( should handle co2e)
                )
            logger.info(
                "Received request for ColourViewset list with location: %s and year: %s",
                location,
                year,
            )
            return Response(result, status=status.HTTP_200_OK)
        except Location.DoesNotExist:
            logger.warning("Location not found: %s", location)
            return Response(
                {"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND
            )
