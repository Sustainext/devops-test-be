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


class SocialNonDiscrimationAnalysis(APIView):
    """
    This class is used to get the social non-discrimination analysis.
    """

    permission_classes = [IsAuthenticated]
    slugs = [
        "gri-social-incidents_of_discrimination-406-1a-incidents_of_discrimination"
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

    def get_incidents_of_discrimination(self):
        """
        This function is used to get the incidents of discrimination.
        """
        incidents_of_discrimination = defaultdict(int)

        data = [
            item
            for raw_response in self.raw_responses.filter(path__slug=self.slugs[0])
            for item in raw_response.data
        ]

        for item in data:
            incidents_of_discrimination[item["typeofincident"]] += int(
                item["totalnumberofincidentsofdiscrimination"]
            )

        return dict(incidents_of_discrimination)

    def get(self, request, format=None):
        """
        This function is used to get the social non-discrimination analysis.
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
            data={
                "incidents_of_discrimination": self.get_incidents_of_discrimination()
            },
            status=status.HTTP_200_OK,
        )
