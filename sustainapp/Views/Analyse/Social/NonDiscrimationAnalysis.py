from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates
from common.utils.get_data_points_as_raw_responses import collect_data_by_raw_response_and_index
from datametric.models import DataPoint, RawResponse
from collections import Counter


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
                    locale=self.location,
                )
            .prefetch_related("path")
            .order_by("-year", "-month")
            .only("data")
        )

    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(client_id=self.request.user.client.id)
            .filter(path__slug__in=self.slugs)
            .filter(filter_by_start_end_dates(self.start, self.end))
            .filter(locale=self.location)
        )
    def get_incidents_of_discrimination(self):
        """
        This function is used to get the incidents of discrimination.
        """
        data = collect_data_by_raw_response_and_index(self.data_points)

        incidents_counter = Counter()
        for item in data:
            incidents_counter[item["typeofincident"]] += int(
                item["totalnumberofincidentsofdiscrimination"]
            )

        return [
            {
                "Type of Incident": incident_type,
                "Total number of Incidents of discrimination": count,
            }
            for incident_type, count in incidents_counter.items()
        ]

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
        self.set_data_points()
        return Response(
            data={
                "incidents_of_discrimination": self.get_incidents_of_discrimination()
            },
            status=status.HTTP_200_OK,
        )
