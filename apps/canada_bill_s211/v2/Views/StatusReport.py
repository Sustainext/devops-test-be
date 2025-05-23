from textwrap import fill
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.serializers.CheckYearOrganisationCorporateSerializer import CheckYearOrganizationCorporateSerializer
from apps.canada_bill_s211.v2.constants import SUBMISSION_INFORMATION, REPORTING_FOR_ENTITIES
from apps.canada_bill_s211.v2.utils.check_status_report import get_status_report_data

class StatusReport(APIView):
    permission_classes = [IsAuthenticated]



    def get(self, request):
        serializer = CheckYearOrganizationCorporateSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        organization = validated_data['organization']
        corporate = validated_data.get("corporate")
        # Check if user has access to the organization
        if not request.user.orgs.filter(id=organization.id).exists():
            return Response(
                {"organization": ["You do not have access to this organization."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has access to the corporate (if provided)
        if corporate is not None and not request.user.corps.filter(id=corporate.id).exists():
            return Response(
                {"corporate": ["You do not have access to this corporate."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        filters = {
            "organization": organization,
            "year": validated_data["year"],
            "organization__client": request.user.client,
        }
        if corporate:
            filters["corporate"] = corporate

        reporting_for_entities_response, submission_information_response = get_status_report_data(filters)

        return Response(
            {
            "reporting_for_entities": reporting_for_entities_response,
            "submission_information": submission_information_response
            }, status=status.HTTP_200_OK)
