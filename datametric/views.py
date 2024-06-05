from rest_framework import generics

# from .models import Transaction
# from .serializers import TransactionSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FieldGroup, Path, RawResponse
from .serializers import (
    FieldGroupSerializer,
    UpdateResponseSerializer,
    RawResponseSerializer,
)
from authentication.models import CustomUser, Client


class TestView(APIView):

    def get(self, request, *args, **kwargs):

        return Response("User created successfully", status=status.HTTP_200_OK)


class FieldGroupListView(APIView):
    def get(self, request, format=None):
        path_slug = request.query_params.get("path", None)
        client_id = request.query_params.get("client_id", None)
        user_id = request.query_params.get("user_id", None)

        if path_slug is None:
            return Response(
                {"error": "Path slug is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            path = Path.objects.get(slug=path_slug)
        except Path.DoesNotExist:
            return Response(
                {"error": "Path not found"}, status=status.HTTP_404_NOT_FOUND
            )

        field_groups = FieldGroup.objects.filter(path=path)
        serialized_field_groups = FieldGroupSerializer(field_groups, many=True)

        # Checking form data if any
        path_instance = Path.objects.get(slug=path_slug)
        user_instance = CustomUser.objects.get(pk=user_id)
        client_instance = Client.objects.get(pk=client_id)
        raw_responses = RawResponse.objects.filter(
            path=path_instance,
            user=user_instance,
            client=client_instance,
        )
        serialized_raw_responses = RawResponseSerializer(raw_responses, many=True)
        resp_data = {}
        resp_data["form"] = serialized_field_groups.data
        resp_data["form_data"] = serialized_raw_responses.data
        return Response(resp_data)


class CreateOrUpdateFieldGroup(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UpdateResponseSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            client_id = validated_data["client_id"]
            user_id = validated_data["user_id"]
            form_data = validated_data["form_data"]
            path = validated_data["path"]
            # schema = validated_data["schema"]

            try:
                # Retrieve instances of related models
                path_instance = Path.objects.get(slug=path)
                user_instance = CustomUser.objects.get(pk=user_id)
                client_instance = Client.objects.get(pk=client_id)

                # Try to get an existing RawResponse instance
                raw_response, created = RawResponse.objects.get_or_create(
                    path=path_instance,
                    user=user_instance,
                    client=client_instance,
                    defaults={"data": form_data},
                )

                if not created:
                    # If the RawResponse already exists, update its data
                    raw_response.data = form_data
                    raw_response.save()
                
                print('status check')
                print(f"RawResponse: {raw_response}")
                print(f"Created: {created}")

                return Response(
                    {"message": "Form data saved successfully."},
                    status=status.HTTP_200_OK,
                )

            except (Path.DoesNotExist, CustomUser.DoesNotExist, Client.DoesNotExist) as e:
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
        else:
            # If serializer is not valid, return the serializer errors
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
