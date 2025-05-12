from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.serializers.SubmissionInformationSerializer import SubmissionInformationSerializer
from apps.canada_bill_s211.v2.serializers.CheckYearOrganisationCorporateSerializer import CheckYearOrganizationCorporateSerializer
from sustainapp.models import Organization
import logging

logger = logging.getLogger("error") # Or a more specific logger if you prefer

class SubmissionInformationView(APIView):
    """
    View for managing submission information data in Canada Bill S211 v2.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, screen_id):
        query_param_serializer = CheckYearOrganizationCorporateSerializer(data=request.GET)
        if not query_param_serializer.is_valid():
            return Response(query_param_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_query_params = query_param_serializer.validated_data
        organization = validated_query_params.get("organization")
        corporate = validated_query_params.get("corporate")

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

        try:
            submission_info = SubmissionInformation.objects.get(
                organization=organization,
                corporate=corporate,
                year=validated_query_params["year"],
                screen=screen_id,
                organization__client=request.user.client
            )
        except SubmissionInformation.DoesNotExist:
            return Response(
                {"message": "Submission Information not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        response_serializer = SubmissionInformationSerializer(submission_info)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, screen_id):
        data_check_serializer = CheckYearOrganizationCorporateSerializer(data=request.data)
        if not data_check_serializer.is_valid():
            return Response(data_check_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = data_check_serializer.validated_data

        organization = validated_data.get("organization")
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

        try:
            # Note: Removed .filter(organization__in=..., corporate__in=...) as checks are done above
            submission_info = SubmissionInformation.objects.get(
                organization=organization,
                corporate=corporate,
                year=validated_data["year"],
                screen=screen_id,
                organization__client=request.user.client
            )

            # Update existing instance
            data = request.data.copy()
            data["screen"] = screen_id # screen_id is already part of the URL, no need to add to data
            serializer = SubmissionInformationSerializer(instance=submission_info, data=data, partial=True) # partial=True added as discussed earlier
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except SubmissionInformation.DoesNotExist:
            # Create new instance
            create_data = request.data.copy()
            create_data["screen"] = screen_id
            serializer = SubmissionInformationSerializer(data=create_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
