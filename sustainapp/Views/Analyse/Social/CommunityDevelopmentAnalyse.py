from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
    safe_integer_divide,
)
from datametric.models import RawResponse
from collections import defaultdict


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

    def get_community_engagement(self):
        # * Making Response like this
        """
        This function is used to get the community engagement.
        """
        local_data = [
            raw_response.data
            for raw_response in self.raw_responses.filter(path__slug=self.slugs[0])
        ]
        response_data = {
            "Social impact assessments": 0,
            "Environmental impact assessments": 0,
            "Public disclosure": 0,
            "Community development programs": 0,
            "Stakeholder engagement plans": 0,
            "Local community consultation committes": 0,
            "works councils, occupational health and safety committees": 0,
            "Community grievance processes": 0,
        }
        sum_of_total_operation = sum(
            [
                sum(int(item["totaloperations"]) for item in sublist)
                for sublist in local_data
            ]
        )

        for each_month_data in local_data:
            response_data["Social impact assessments"] += int(
                each_month_data[0]["operations"]
            )
            response_data["Environmental impact assessments"] += int(
                each_month_data[1]["operations"]
            )
            response_data["Public disclosure"] += int(each_month_data[2]["operations"])
            response_data["Community development programs"] += int(
                each_month_data[3]["operations"]
            )
            response_data["Stakeholder engagement plans"] += int(
                each_month_data[4]["operations"]
            )
            response_data["Local community consultation committes"] += int(
                each_month_data[5]["operations"]
            )
            response_data[
                "works councils, occupational health and safety committees"
            ] += int(each_month_data[6]["operations"])
            response_data["Community grievance processes"] += int(
                each_month_data[7]["operations"]
            )
        response_data_list = []
        for key, value in response_data.items():
            response_data[key] = safe_integer_divide(value, sum_of_total_operation)
        for key, value in response_data.items():
            response_data_list.append(
                {
                    "": key,
                    "Percentage of operations implemented by engaging local communities": value,
                }
            )
        return response_data_list

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
        self.set_raw_responses()
        return Response(
            {
                "community_engagement": self.get_community_engagement(),
            },
            status=status.HTTP_200_OK,
        )
