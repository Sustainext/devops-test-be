from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    set_locations_data,
    get_raw_response_filters,
)
from datametric.models import RawResponse, DataPoint
from sustainapp.Utilities.community_engagement_analysis import (
    get_community_engagement_analysis,
)
from collections import defaultdict
from common.utils.value_types import safe_percentage
from logging import getLogger

logger = getLogger("error.log")


class SocialHumanRightsAndCommunityImpactAnalysis(APIView):
    """
    This class is used to get the community engagement analysis and security personnel analysis.
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

    def analyse_security_perrsonnel(self, start_date, end_date, path):
        # get all data points for the given path
        data_points = DataPoint.objects.filter(
            locale__in=self.locations,
            path__slug=path,
            client_id=self.request.user.client.id,
        ).filter(filter_by_start_end_dates(start_date=start_date, end_date=end_date))

        if not data_points:
            return []

        indexed_data = defaultdict(lambda: defaultdict(dict))

        for dp in data_points:
            if dp.raw_response and dp.index is not None:
                # Ensure that we have a dictionary to update at each level
                indexed_data[dp.raw_response.id][dp.index].update(
                    {dp.metric_name: dp.value}
                )

        grouped_data = []
        for key, op in indexed_data.items():
            for sub_value in op.values():
                try:
                    securitypersonnel = float(sub_value.get("securitypersonnel"))
                    organization = (
                        float(sub_value.get("organization", 0))
                        if sub_value.get("organization")
                        else 0
                    )
                    thirdpartyorganizations = (
                        float(sub_value.get("thirdpartyorganizations", 0))
                        if sub_value.get("thirdpartyorganizations")
                        else 0
                    )

                    grouped_data.append(
                        {
                            "sp_in_org": (
                                safe_percentage(organization, securitypersonnel)
                            ),
                            "sp_3rd_org": (
                                safe_percentage(
                                    thirdpartyorganizations, securitypersonnel
                                )
                            ),
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error occrued while analyzing Security Personnel : {e}"
                    )
        return grouped_data

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
        self.locations = set_locations_data(
            self.organisation, self.corporate, self.location
        )
        security_personnel = self.analyse_security_perrsonnel(
            self.start,
            self.end,
            "gri-social-human_rights-410-1a-security_personnel",
        )

        return Response(
            {
                "security_personnel": security_personnel,
                "community_engagement": community_engagement_data,
            },
            status=status.HTTP_200_OK,
        )
