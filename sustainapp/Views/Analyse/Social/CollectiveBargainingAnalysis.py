from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates, get_raw_response_filters
from datametric.models import RawResponse
from collections import defaultdict


class SocialCollectiveBargainingAnalysis(APIView):
    """
    This class is used to get the social collective bargaining analysis.
    """

    permission_classes = [IsAuthenticated]
    slugs = [
        "gri-social-collective_bargaining-407-1a-operations",
        "gri-social-collective_bargaining-407-1a-suppliers",
    ]

    def set_raw_responses(self):
        user = self.request.user
        self.raw_responses = (
            RawResponse.objects.filter(client=user.client)
            .filter(path__slug__in=self.slugs)
            .filter(year__range=(self.start.year, self.end.year))
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .prefetch_related("path")
            .order_by("-year", "-month")
            .only("data")
        )

    def get_operation_bargaining(self):
        slug = self.slugs[0]
        return [
            {
                "Operations in which workers' rights to exercise freedom of association or collective bargaining may be violated or at significant risk": item[
                    "significantrisk"
                ],
                "Type of Operation": item["TypeofOperation"],
                "Countries or Geographic Areas": item["geographicareas"],
            }
            for raw_response in self.raw_responses.filter(path__slug=slug)
            for item in raw_response.data
        ]

    def get_supplier_bargaining(self):
        slug = self.slugs[1]
        return [
            {
                "Suppliers in which workers' rights to exercise freedom of association or collective bargaining may be violated or at significant risk": item[
                    "significantrisk"
                ],
                "Type of Supplier": item["TypeofOperation"],
                "Countries or Geographic Areas": item["geographicareas"],
            }
            for raw_response in self.raw_responses.filter(path__slug=slug)
            for item in raw_response.data
        ]

    def get(self, request, format=None):
        """
        This function is used to get the collective bargaining analysis.
        """
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.set_raw_responses()
        return Response(
            {
                "operation_bargaining": self.get_operation_bargaining(),
                "supplier_bargaining": self.get_supplier_bargaining(),
            },
            status=status.HTTP_200_OK,
        )
