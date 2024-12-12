from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from canadabills211.models.CanadaBillS211 import (
    IdentifyingInformation,
)
from canadabills211.Serializers.CanadaBillS211Serializer import (
    IISerializer,
)
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger("error.log")


class IIScreenViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        client_id = request.user.client.id
        org_id = request.query_params["org_id"]
        corp_id = request.query_params.get("corp_id", None)
        corp_id = corp_id if corp_id else None
        year = request.query_params["year"]
        try:
            identifying_info = IdentifyingInformation.objects.get(
                organization_id=org_id,
                corporate_id=corp_id,
                year=year,
                client_id=client_id,
            )
        except IdentifyingInformation.DoesNotExist:
            return Response(
                {
                    "detail": f"There is no data for the organization with the id {org_id} and the corporate {corp_id} the year {year}"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer_class = self.get_serializer_class()
        if serializer_class is None:
            return Response(
                {"detail": "Please check the screen number"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializer_class(identifying_info)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        client_id = request.user.client.id
        org_id = request.data["organization_id"]
        corp_id = request.data["corporate_id"]
        year = request.data["year"]
        request.data["user_id"] = request.user.id
        try:
            identifying_info = IdentifyingInformation.objects.get(
                organization_id=org_id,
                corporate_id=corp_id,
                year=year,
                client_id=client_id,
            )
        except IdentifyingInformation.DoesNotExist:
            identifying_info = None
        logger.error(f"Identifying info is {identifying_info}")
        if identifying_info is None:
            # If instance does not exist, create a new instance
            serializer_class = self.get_serializer_class()
            if serializer_class is None:
                return Response(
                    {"detail": "Please check the screen number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                response_data = serializer.data
                response_data["id"] = instance.id
                return Response(response_data, status=status.HTTP_200_OK)  # 200 ok
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If instance exists, update the existing instance
            serializer_class = self.get_serializer_class()
            if serializer_class is None:
                return Response(
                    {"detail": "Please check the screen number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer_class(instance=identifying_info, data=request.data)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                response_data = serializer.data
                response_data["id"] = instance.id
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        screen_number = self.request.query_params.get("screen")
        logger.error(
            f"the screen number in the get-serializer-class is {screen_number} and the type is {type(screen_number)}"
        )
        return lambda *args, **kwargs: IISerializer(
            *args, **kwargs, screen_number=screen_number
        )
