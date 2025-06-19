from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.tcfd_framework.models.TCFDCollectModels import (
    SelectedDisclosures,
)
from apps.tcfd_framework.models.TCFDReportingModels import TCFDReportingInformation
from apps.tcfd_framework.serializers.RecommendedDisclosuresListSerializer import (
    RecommendedDisclosureIdListSerializer,
)
from apps.tcfd_framework.serializers.TCFDReportingInformationSerializer import (
    TCFDReportingInformationBasicSerializer,
)
from apps.tcfd_framework.utils import (
    get_or_set_tcfd_cache_data,
    update_selected_disclosures_cache,
    get_user_framework_data,
)
from django.db.models import Q
import logging

logger = logging.getLogger("django")


class GetTCFDDisclosures(APIView):
    """
    This view gets the core elements and recommended disclosures for TCFD Collect Section.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # * Get Selected Disclosures
        basic_serializer = TCFDReportingInformationBasicSerializer(
            data=request.query_params
        )
        basic_serializer.is_valid(raise_exception=True)
        organization = basic_serializer.validated_data["organization"]
        corporate = basic_serializer.validated_data.get("corporate", None)
        response_data = get_or_set_tcfd_cache_data(
            organization=organization, corporate=corporate
        )
        return Response(
            data={
                "message": "Core elements and recommended disclosures fetched successfully.",
                "data": response_data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class UpdateSelectedDisclosures(APIView):
    """
    This view gets or updates the selected disclosures for TCFD Collect Section.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = RecommendedDisclosureIdListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recommended_disclosures = serializer.validated_data["recommended_disclosures"]
        organization = serializer.validated_data["organization"]
        corporate = serializer.validated_data.get("corporate", None)
        response_data = update_selected_disclosures_cache(
            organization=organization,
            corporate=corporate,
            recommended_disclosures=recommended_disclosures,
        )

        return Response(
            data={
                "message": {
                    "header": "TCFD Disclosure Selection Updated",
                    "body": "TCFD Disclosures has been selected and saved successfully.",
                    "gradient": "linear-gradient(to right, #00AEEF, #6ADF23)",
                },
                "data": response_data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class GetLatestSelectedDisclosures(APIView):
    """
    This view gets the latest selected disclosures for TCFD Collect Section.
    """

    permission_classes = [IsAuthenticated]

    def filter_selected_disclosures(self, data):
        filtered_data = {}
        for section, content in data.items():
            filtered_disclosures = [
                d for d in content.get("disclosures", []) if d.get("selected") is True
            ]
            if filtered_disclosures:
                filtered_data[section] = {
                    "description": content.get("description"),
                    "disclosures": filtered_disclosures,
                }
        return filtered_data

    def get(self, request, *args, **kwargs):
        user = request.user
        filters = Q(
            organization__in=user.orgs.all(), corporate__in=user.corps.all()
        ) | Q(organization__in=user.orgs.all(), corporate__isnull=True)

        selected_disclosure = (
            SelectedDisclosures.objects.filter(filters).order_by("-updated_at").first()
        )
        tcfd_info = (
            TCFDReportingInformation.objects.filter(filters)
            .order_by("-updated_at")
            .first()
        )

        # Framework caching as a helper utility call
        framework_data = get_user_framework_data(user)

        response_data = None
        if selected_disclosure:
            response_data = get_or_set_tcfd_cache_data(
                organization=selected_disclosure.organization,
                corporate=selected_disclosure.corporate,
            )

        return Response(
            {
                "message": "Only Latest Selected Disclosures fetched.",
                "data": {
                    "framework_data": framework_data,
                    "selected_disclosures": self.filter_selected_disclosures(
                        response_data
                    )
                    if response_data
                    else None,
                    "tcfd_reporting_information_sector": getattr(
                        tcfd_info, "sector", None
                    ),
                    "tcfd_reporting_information_sector_type": getattr(
                        tcfd_info, "sector_type", None
                    ),
                },
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
