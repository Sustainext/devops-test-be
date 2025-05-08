from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from apps.canada_bill_s211.v2.serializers.ReportingForEntitiesSerializer import ReportingForEntitiesSerializer
from apps.canada_bill_s211.v2.serializers.CheckYearOrganisationCorporateSerializer import CheckYearOrganizationCorporateSerializer
from django.db.models import Q
import logging

from sustainapp.models import Organization
logger = logging.getLogger("error")

class ReportingForEntitiesView(APIView):
    """
    View for managing reporting data for entities in Canada Bill S211 v2.
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
            report_entity = ReportingForEntities.objects.get(
                organization=validated_query_params["organization"],
                corporate=validated_query_params.get("corporate"),
                year=validated_query_params["year"],
                screen=screen_id,  # Assuming your model field is 'screen'
                organization__client=request.user.client
            )

        except ReportingForEntities.DoesNotExist:
            return Response(
                {"error": "Reporting data not found or access denied for the specified criteria."},
                status=status.HTTP_404_NOT_FOUND
            )
        response_serializer = ReportingForEntitiesSerializer(report_entity)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, screen_id):
        #* Check if Reporting For Entities exists
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
            reporting_for_entities = ReportingForEntities.objects.get(
                organization=data_check_serializer.validated_data["organization"],
                corporate=data_check_serializer.validated_data.get("corporate"),
                year=data_check_serializer.validated_data["year"],
                screen=screen_id,
                organization__client=request.user.client
            )
            data = request.data.copy()
            data["screen"] = screen_id
            serializer = ReportingForEntitiesSerializer(instance=reporting_for_entities, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReportingForEntities.DoesNotExist as e:
            logger.error(f"ReportingForEntities.DoesNotExist: {e}",exc_info=True)
            #* Create a Reporting For Entities
            data = request.data.copy()
            data["screen"] = screen_id
            serializer = ReportingForEntitiesSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
