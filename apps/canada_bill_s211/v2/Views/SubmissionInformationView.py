from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.serializers.SubmissionInformationSerializer import SubmissionInformationSerializer
from apps.canada_bill_s211.v2.serializers.CheckYearOrganisationCorporateSerializer import CheckYearOrganizationCorporateSerializer
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

        try:
            submission_info = SubmissionInformation.objects.get(
                organization=validated_query_params["organization"],
                corporate=validated_query_params.get("corporate"),
                year=validated_query_params["year"],
                screen=screen_id,
                organization__in=request.user.orgs.all(),
                corporate__in=request.user.corps.all(), # Assuming similar permission logic
                organization__client=request.user.client
            )
        except SubmissionInformation.DoesNotExist:
            return Response(
                {"error": "Submission Information not found or access denied for the specified criteria."},
                status=status.HTTP_404_NOT_FOUND
            )

        response_serializer = SubmissionInformationSerializer(submission_info)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, screen_id):
        data_check_serializer = CheckYearOrganizationCorporateSerializer(data=request.data)
        if not data_check_serializer.is_valid():
            return Response(data_check_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data_for_check = data_check_serializer.validated_data

        try:
            submission_info = SubmissionInformation.objects.filter(
                organization__in=request.user.orgs.all(),
                corporate__in=request.user.corps.all()
            ).get(
                organization=validated_data_for_check["organization"],
                corporate=validated_data_for_check.get("corporate"),
                year=validated_data_for_check["year"],
                screen=screen_id,
                organization__client=request.user.client
            )

            # Update existing instance
            serializer = SubmissionInformationSerializer(instance=submission_info, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except SubmissionInformation.DoesNotExist:
            # Create new instance
            # Note: The SubmissionInformation model provided doesn't have the same unique_together constraint
            # as ReportingForEntities (['organization', 'corporate', 'year', 'screen']).
            # If it should, add it to the SubmissionInformation model's Meta class.
            # The current logic will simply create if not found.

            create_data = request.data.copy()
            create_data["screen"] = screen_id
            serializer = SubmissionInformationSerializer(data=create_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in SubmissionInformationView PUT: {e}", exc_info=True)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
