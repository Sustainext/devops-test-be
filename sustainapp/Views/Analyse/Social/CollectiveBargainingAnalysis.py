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
            .filter(filter_by_start_end_dates(self.start, self.end))
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

    def get_bargaining(self, slug):
        data = [
            item
            for raw_response in self.raw_responses.filter(path__slug=slug)
            for item in raw_response.data
        ]
        return data

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
                "operations_where_workers_freedom_of_association_or_collective_bargaining_is_at_risk": self.get_bargaining(
                    self.slugs[0]
                ),
                "suppliers_in_which_the_right_to_freedom_of_association_or_collective_bargaining_may_be_at_risk": self.get_bargaining(
                    self.slugs[1]
                ),
            },
            status=status.HTTP_200_OK,
        )
