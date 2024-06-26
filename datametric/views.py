from rest_framework import generics

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FieldGroup, Path, RawResponse, DataPoint
from .serializers import (
    FieldGroupSerializer,
    UpdateResponseSerializer,
    RawResponseSerializer,
    FieldGroupGetSerializer,
    GetClimatiqComputedSerializer
)
from authentication.models import CustomUser, Client
from rest_framework.permissions import IsAuthenticated


class TestView(APIView):

    def get(self, request, *args, **kwargs):
        return Response("User created successfully", status=status.HTTP_200_OK)


class FieldGroupListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        validation_serializer = FieldGroupGetSerializer(data=request.query_params)
        validation_serializer.is_valid(raise_exception=True)
        path_slug = validation_serializer.validated_data.get("path_slug")
        location = validation_serializer.validated_data.get("location")
        year = validation_serializer.validated_data.get("year")
        month = validation_serializer.validated_data.get("month")

        try:
            path = Path.objects.get(slug=path_slug)
        except Path.DoesNotExist:
            return Response(
                {"error": "Path not found"}, status=status.HTTP_404_NOT_FOUND
            )

        field_groups = FieldGroup.objects.filter(path=path)
        serialized_field_groups = FieldGroupSerializer(field_groups, many=True)

        # Checking form data if any
        path_instance = path
        user_instance: CustomUser = self.request.user
        client_instance = user_instance.client
        raw_responses = RawResponse.objects.filter(
            path=path_instance,
            user=user_instance,
            client=client_instance,
            location=location,
            year=year,
            month=month,
        )
        serialized_raw_responses = RawResponseSerializer(raw_responses, many=True)
        resp_data = {}
        resp_data["form"] = serialized_field_groups.data
        resp_data["form_data"] = serialized_raw_responses.data
        return Response(resp_data)


class CreateOrUpdateFieldGroup(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = UpdateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        form_data = validated_data["form_data"]
        path = validated_data["path"]
        location = validated_data["location"]
        year = validated_data["year"]
        month = validated_data["month"]

        try:
            # Retrieve instances of related models
            path_instance = Path.objects.get(slug=path)
            user_instance:CustomUser = self.request.user
            client_instance = user_instance.client

            # Try to get an existing RawResponse instance
            raw_response, created = RawResponse.objects.get_or_create(
                path=path_instance,
                user=user_instance,
                client=client_instance,
                location=location,
                year=year,
                month=month,
                defaults={"data": form_data},
            )

            if not created:
                # If the RawResponse already exists, update its data
                raw_response.data = form_data
                raw_response.save()

            print("status check")
            print(f"RawResponse: {raw_response}")
            print(f"Created: {created}")

            return Response(
                {"message": "Form data saved successfully."},
                status=status.HTTP_200_OK,
            )

        except (
            Path.DoesNotExist,
            CustomUser.DoesNotExist,
            Client.DoesNotExist,
        ) as e:
            print(f"Lookup error: {e}")
            return Response(
                {"message": "Path, User, or Client does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response(
                {"message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class GetComputedClimatiqValue(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        validation_serializer = GetClimatiqComputedSerializer(data=request.query_params)
        validation_serializer.is_valid(raise_exception=True)
        location = validation_serializer.validated_data.get("location")
        year = validation_serializer.validated_data.get("year")
        month = validation_serializer.validated_data.get("month")
        user_instance: CustomUser = self.request.user
        client_instance = user_instance.client
        path = Path.objects.filter(slug='gri-collect-emissions-scope-combined').first()
        try:
            datapoint = DataPoint.objects.filter(
                user_id=user_instance.id,
                client_id=client_instance.id,
                month=month,
                year=year,
                location=location,
                path=path
            ).first()
            resp_data = {}
            resp_data["result"] = datapoint.json_holder
            return Response(resp_data,status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Exception occurred: {e}")
            return Response(
                {"message": "An unexpected error occurred for GetComputedClimatiqValue "},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )