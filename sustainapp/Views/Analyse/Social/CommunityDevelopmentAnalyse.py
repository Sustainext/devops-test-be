from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates, get_raw_response_filters
from datametric.models import RawResponse
from sustainapp.Utilities.community_engagement_analysis import (
    get_community_engagement_analysis,
)


class SocialCommunityDevelopmentAnalysis(APIView):
    """
    This class is used to get the social community development analysis.
    """

    permission_classes = [IsAuthenticated]
    slugs = ["gri-social-community_engagement-413-1a-number_of_operations"]

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

    def get(self, request, format=None):
        """
        This function is used to get the social community development analysis.
        """
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")

        # Set the raw responses
        self.set_raw_responses()

        # Get the community engagement analysis using the service
        community_engagement_data = get_community_engagement_analysis(
            raw_responses=self.raw_responses, slugs=self.slugs
        )

        return Response(
            {
                "community_engagement": community_engagement_data,
            },
            status=status.HTTP_200_OK,
        )
