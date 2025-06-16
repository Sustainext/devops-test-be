from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from apps.tcfd_framework.models.TCFDReportingModels import TCFDReportingInformation
from apps.tcfd_framework.models.TCFDCollectModels import SelectedDisclosures
from apps.tcfd_framework.serializers.TCFDReportingInformationSerializer import (
    TCFDReportingInformationBasicSerializer,
)


class TCFDStatusCompletionView(APIView):
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
            selected_disclosure_status = SelectedDisclosures.objects.filter(
                organization=organization, corporate=corporate
            ).exists()
            return Response(
                {
                    "tcfd_reporting_info_status": reporting_info.status,
                    "tcfd_selected_disclosure_status": selected_disclosure_status,
                },
                status=status.HTTP_200_OK,
            )
        except TCFDReportingInformation.DoesNotExist:
            return Response(
                {
                    "tcfd_reporting_info_status": False,
                    "tcfd_selected_disclosure_status": False,
                    "errors": {"detail": "Not found."},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
