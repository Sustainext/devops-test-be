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
from apps.tcfd_framework.utils import get_tcfd_disclosures_response


class GetTCFDDisclosures(APIView):
    """
    This view gets the core elements and recommended disclosures for TCFD Collect Section.
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_mapping = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h",
            8: "i",
            9: "j",
            10: "k",
        }

    def get(self, request, *args, **kwargs):
        # * Get all important data
        disclosures = RecommendedDisclosures.objects.select_related("core_element")

        return Response(
            data={
                "message": "Core elements and recommended disclosures fetched successfully.",
                "data": get_tcfd_disclosures_response(disclosures_queryset=disclosures),
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
        )
        if corporate:
            selected_disclosures = selected_disclosures.filter(corporate=corporate)
        selected_disclosures.delete()
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

        return Response(
            data={
                "message": "Selected disclosures updated successfully.",
                "data": get_tcfd_disclosures_response(
                    disclosures_queryset=RecommendedDisclosures.objects.filter(
                        id__in=SelectedDisclosures.objects.filter(
                            organization=organization,
                            corporate=corporate,
                        ).values_list("recommended_disclosure_id", flat=True)
                    ).select_related("core_element")
                ),
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request, *args, **kwargs):
        serializer = TCFDReportingInformationBasicSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data["organization"]
        corporate = serializer.validated_data.get("corporate", None)
        selected_disclosures = SelectedDisclosures.objects.filter(
            organization=organization,
            corporate=corporate
        )
        recommended_disclosures = RecommendedDisclosures.objects.filter(
            id__in=selected_disclosures.values_list(
                "recommended_disclosure_id", flat=True
            )
        ).select_related("core_element")
        return Response(
            data={
                "message": "Selected disclosures fetched successfully.",
                "data": get_tcfd_disclosures_response(
                    disclosures_queryset=recommended_disclosures
                ),
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
