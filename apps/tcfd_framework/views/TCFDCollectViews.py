from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.tcfd_framework.models.TCFDCollectModels import (
    CoreElements,
    RecommendedDisclosures,
    DataCollectionScreen,
    SelectedDisclosures,
)
from apps.tcfd_framework.serializers.RecommendedDisclosuresListSerializer import (
    RecommendedDisclosureIdListSerializer,
)
from apps.tcfd_framework.serializers.TCFDReportingInformationSerializer import (
    TCFDReportingInformationBasicSerializer,
)

from collections import defaultdict
from django.core.cache import cache
from apps.tcfd_framework.utils import get_tcfd_disclosures_response
from common.utils.sanitise_cache import sanitize_cache_key_part


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
        cache_key = f"tcfd_disclosures_{sanitize_cache_key_part(organization)}_{sanitize_cache_key_part(corporate)}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            selected_disclosures = SelectedDisclosures.objects.filter(
                organization=organization, corporate=corporate
            ).prefetch_related("recommended_disclosure")
            selected_disclosures_recommended_disclosure_ids = (
                selected_disclosures.values_list(
                    "recommended_disclosure__id", flat=True
                )
            )

            # * Get all important data
            disclosures = RecommendedDisclosures.objects.select_related("core_element")
            response_data = get_tcfd_disclosures_response(
                disclosures_queryset=disclosures,
                selected_disclosures_ids=selected_disclosures_recommended_disclosure_ids,
            )
            cache.set(cache_key, response_data, timeout=86400)
        else:
            response_data = cached_data
        return Response(
            data={
                "message": "Core elements and recommended disclosures fetched successfully.",
                "data": response_data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class GetOrUpdateSelectedDisclosures(APIView):
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
        selected_disclosures = SelectedDisclosures.objects.filter(
            recommended_disclosure__in=recommended_disclosures,
            organization=organization,
            corporate=corporate,
        )
        selected_disclosures.delete()
        cache_key = f"tcfd_disclosures_{sanitize_cache_key_part(organization)}_{sanitize_cache_key_part(corporate)}"
        cache.delete(cache_key)

        selected_disclosures = SelectedDisclosures.objects.bulk_create(
            [
                SelectedDisclosures(
                    recommended_disclosure=rd,
                    organization=organization,
                    corporate=corporate,
                )
                for rd in recommended_disclosures
            ]
        )
        response_data = get_tcfd_disclosures_response(
            disclosures_queryset=RecommendedDisclosures.objects.filter(
                id__in=SelectedDisclosures.objects.filter(
                    organization=organization,
                    corporate=corporate,
                ).values_list("recommended_disclosure_id", flat=True)
            ).select_related("core_element")
        )
        cache.set(cache_key, response_data, timeout=86400)

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
