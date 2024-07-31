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
        #* Making Response like this
        [
            {
                "": "Percentage of Security Personnel (in organisation)",
                "Percentage of operations implemented by engaging local communities": "",
            },
            {
                "": "Environmental impact assessments",
                "Percentage of operations implemented by engaging local communities": "",
            },
            {
                "": "Public disclosure",
                "Percentage of operations implemented by engaging local communities": "",
            },
            {
                "": "Community development programs",
                "Percentage of operations implemented by engaging local communities": "",
            },
            {
                "": "Stakeholder engagement plans",
                "Percentage of operations implemented by engaging local communities": "",
            },
            {
                "": "Local community consultation committes",
                "Percentage of operations implemented by engaging local communities": "",
            },
        ]
        """
        This function is used to get the community engagement.
        """
        local_data = [
            raw_response.data
            for raw_response in self.raw_responses.filter(path__slug=self.slugs[0])
        ]
        response_data = {
            "social_impact_assessments": 0,
            "environmental_impact_assessments": 0,
            "public_disclosure": 0,
            "community_development_programs": 0,
            "stakeholder_engagement_plans": 0,
            "local_community_consultation_committes": 0,
            "works_councils_occupational_health_and_safety_committees": 0,
            "community_grievance_processes": 0,
        }
        sum_of_total_operation = sum(
            [
                sum(int(item["totaloperations"]) for item in sublist)
                for sublist in local_data
            ]
        )

        for each_month_data in local_data:
            response_data["social_impact_assessments"] += int(
                each_month_data[0]["operations"]
            )
            response_data["environmental_impact_assessments"] += int(
                each_month_data[1]["operations"]
            )
            response_data["public_disclosure"] += int(each_month_data[2]["operations"])
            response_data["community_development_programs"] += int(
                each_month_data[3]["operations"]
            )
            response_data["stakeholder_engagement_plans"] += int(
                each_month_data[4]["operations"]
            )
            response_data["local_community_consultation_committes"] += int(
                each_month_data[5]["operations"]
            )
            response_data[
                "works_councils_occupational_health_and_safety_committees"
            ] += int(each_month_data[6]["operations"])
            response_data["community_grievance_processes"] += int(
                each_month_data[7]["operations"]
            )
        for key, value in response_data.items():
            response_data[key] = safe_integer_divide(value, sum_of_total_operation)
        return response_data

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
