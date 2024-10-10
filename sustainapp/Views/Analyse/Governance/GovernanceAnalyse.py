from datametric.models import RawResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import get_raw_response_filters
from common.utils.value_types import get_decimal
from sustainapp.utils import (
    get_ratio_of_annual_total_compensation_ratio_of_percentage_increase_in_annual_total_compensation,
)


class GovernanceAnalyse(APIView):
    permission_classes = [IsAuthenticated]

    slugs = [
        "gri-governance-compensation_ratio-2-21-a-annual",
        "gri-governance-compensation_ratio-2-21-b-percentage",
    ]

    def set_raw_responses(self):
        user = self.request.user
        self.raw_response = (
            RawResponse.objects.filter(
                path__slug__in=self.slugs,
                client=user.client,
            )
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
        )

    def get_analyse_data(
        self,
    ):
        return get_ratio_of_annual_total_compensation_ratio_of_percentage_increase_in_annual_total_compensation(
            raw_response=self.raw_response, slugs=self.slugs
        )

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.set_raw_responses()
        response_data = {
            "compensation_ratio_annual_total_and_increase": self.get_analyse_data()
        }
        return Response(response_data, status=status.HTTP_200_OK)
