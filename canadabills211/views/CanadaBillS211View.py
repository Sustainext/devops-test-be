from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, serializers
from canadabills211.models.CanadaBillS211 import IdentifyingInformation, AnnualReport
from canadabills211.Serializers.CanadaBillS211Serializer import (
    IISerializer,
    ARSerializer,
)
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Corporateentity
import logging

logger = logging.getLogger("error.log")

class CanadaBillS211Viewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    model = None
    serializer = None

    def get_queryset(self):
        if not self.model:
            raise NotImplementedError("Model is not defined for this viewset.")

        self.client_id = self.request.user.client.id
        self.screen_number = self.request.query_params["screen"]
        if self.request.method == "GET":
            self.org_id = self.request.query_params["org_id"]
            self.corp_id = self.request.query_params.get("corp_id")
            self.corp_id = self.corp_id if self.corp_id else None
            self.year = self.request.query_params["year"]
        elif self.request.method in ["POST", "PUT", "PATCH"]:
            self.org_id = self.request.data["organization_id"]
            self.corp_id = self.request.data.get("corporate_id", None)
            self.year = self.request.data["year"]
        else:
            raise serializers.ValidationError(
                {"detail": "Unsupported HTTP method for this operation."}
            )

        if not self.org_id or not self.year:
            raise serializers.ValidationError("`org_id` and `year` are required.")

        try:
            return self.model.objects.get(
                organization_id=self.org_id,
                corporate_id=self.corp_id,
                year=self.year,
                client_id=self.client_id,
            )
        except self.model.DoesNotExist:
            return None

    def list(self, request):
        queryset = self.get_queryset()
        if self.corp_id:
            try:
                Corporateentity.objects.get(
                    id=self.corp_id, organization_id=self.org_id
                )
            except Exception as e:
                return Response(
                    {
                        "error": f"Corporate entity not found for organization_id={self.org_id} and corporate_id={self.corp_id}",
                        "exception": str(e),
                    },
                    status=status.HTTP_200_OK,
                )

        serializer_class = self.serializer
        serializer = serializer_class(queryset, screen_number=self.screen_number)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data["user_id"] = request.user.id
        queryset = self.get_queryset()
        if not queryset:
            # If instance does not exist, create a new instance
            serializer_class = self.serializer
            if serializer_class is None:
                return Response(
                    {"detail": "Please check the screen number."},
                    status=status.HTTP_200_OK,
                )
            serializer = serializer_class(
                data=request.data, screen_number=self.screen_number
            )
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                response_data = serializer.data
                response_data["id"] = instance.id
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If instance exists, update the existing instance
            serializer_class = self.serializer
            if serializer_class is None:
                return Response(
                    {"detail": "Please check the screen number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer_class(
                instance=queryset, data=request.data, screen_number=self.screen_number
            )
            if serializer.is_valid(raise_exception=True):
                instance_saved = serializer.save()
                response_data = serializer.data
                response_data["id"] = instance_saved.id
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IIScreenViewset(CanadaBillS211Viewset):
    model = IdentifyingInformation
    serializer = IISerializer


class ARScreenViewset(CanadaBillS211Viewset):
    model = AnnualReport
    serializer = ARSerializer
