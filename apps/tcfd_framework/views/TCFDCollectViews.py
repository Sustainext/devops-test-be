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
from collections import defaultdict


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
        disclosures = RecommendedDisclosures.objects.select_related(
            "core_element"
        ).values(
            "core_element__id",
            "core_element__name",
            "core_element__description",
            "description",
            "order",
            "screen_tag",
            "id",
        )

        # * Set a default dictionary for handling description and disclosures
        core_map = defaultdict(lambda: {"description": "", "disclosures": []})
        for d in disclosures:
            # * Map based on core_element id
            core_id = d["core_element__id"]

            # * Add description of core_element.
            core_map[core_id]["description"] = d["core_element__description"]

            # * If key "name" is not set, set it to d["core_element__name"] else ignore.
            core_map[core_id].setdefault("name", d["core_element__name"])
            core_map[core_id]["disclosures"].append(
                {
                    "description": f"{self.order_mappping[d['order']]}) {d['description']}",
                    "screen_tag": d["screen_tag"],
                    "id": d["id"],
                }
            )

        response = {
            core["name"]: {
                "description": core["description"],
                "disclosures": core["disclosures"],
            }
            for core in core_map.values()
        }
        return Response(
            data={
                "message": "Core elements and recommended disclosures fetched successfully.",
                "data": response,
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
                    recommended_disclosure_id=rd,
                    organization=organization,
                    corporate=corporate,
                )
                for rd in recommended_disclosures
            ]
        )
        return Response(
            data={
                "message": "Selected disclosures updated successfully.",
                "data": RecommendedDisclosureIdListSerializer(
                    selected_disclosures, many=True
                ).data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request, *args, **kwargs):
        ...
