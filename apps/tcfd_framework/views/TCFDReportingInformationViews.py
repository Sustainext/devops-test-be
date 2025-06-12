from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.tcfd_framework.models.TCFDReportingModels import TCFDReportingInformation
from apps.tcfd_framework.serializers.TCFDReportingInformationSerializer import (
    TCFDReportingInformationSerializer,
    TCFDReportingInformationBasicSerializer,
)
from rest_framework.exceptions import ValidationError as RestFrameworkValidationError


class TCFDReportingInformationView(APIView):
    """
    Handles the retrieval and updating of TCFD Reporting Information for a given client, organization, and corporate.
    This view allows authenticated users to retrieve existing TCFD Reporting Information or create/update it.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve TCFD Reporting Information for the given client, organization, and corporate.
        """
        client = request.user.client
        basic_serializer = TCFDReportingInformationBasicSerializer(
            data=request.query_params
        )
        if not basic_serializer.is_valid():
            return Response(basic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        organization = basic_serializer.validated_data.get("organization")
        corporate = basic_serializer.validated_data.get("corporate")

        try:
            reporting_info = TCFDReportingInformation.objects.get(
                client=client,
                organization=organization,
                corporate=corporate,
            )
            serializer = TCFDReportingInformationSerializer(reporting_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TCFDReportingInformation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        """
        Update or Create TCFD Reporting Information.
        If TCFDReportingInformation exists for the given client and organization, and corporate, update it
        otherwise create a new one.
        """
        client = request.user.client
        basic_serializer = TCFDReportingInformationBasicSerializer(data=request.data)
        if not basic_serializer.is_valid():
            return Response(basic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        organization = basic_serializer.validated_data.get("organization")
        corporate = basic_serializer.validated_data.get("corporate")

        try:
            reporting_info = TCFDReportingInformation.objects.get(
                client=client,
                organization=organization,
                corporate=corporate,
            )
            serializer = TCFDReportingInformationSerializer(
                reporting_info, data=request.data, partial=True
            )
        except TCFDReportingInformation.DoesNotExist:
            serializer = TCFDReportingInformationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(client=client)
            return Response(
                {
                    "message": {
                        "header": "TCFD reporting Information Updated",
                        "body": "Data for the TCFD reporting Information has been added and saved successfully.",
                        "gradient": "linear-gradient(to right, #00AEEF, #6ADF23)",
                    },
                    "data": serializer.data,
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TCFDReportingInformationCompletionView(APIView):
    """
    Checks whether the TCFD Reporting Information for a given organization and corporate is complete or not.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Check if TCFDReportingInformation for given organization and corporate is completed.
        """
        client = request.user.client
        basic_serializer = TCFDReportingInformationBasicSerializer(
            data=request.query_params
        )
        if not basic_serializer.is_valid():
            return Response(basic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        organization = basic_serializer.validated_data.get("organization")
        corporate = basic_serializer.validated_data.get("corporate")

        try:
            reporting_info = TCFDReportingInformation.objects.get(
                client=client,
                organization=organization,
                corporate=corporate,
            )
            try:
                return Response(
                    {"status": reporting_info.status}, status=status.HTTP_200_OK
                )
            except RestFrameworkValidationError as e:
                return Response(
                    {"status": False, "errors": e.detail},
                    status=status.HTTP_200_OK,
                )
        except TCFDReportingInformation.DoesNotExist:
            return Response(
                {"status": False, "errors": {"detail": "Not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
