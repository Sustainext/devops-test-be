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
        """
        This function is used to get the community engagement.
        """
        """
        Example of local data
        [
        0,12    {"operations": "100", "totaloperations": "101"},
        1,13    {"operations": "200", "totaloperations": "201"},
        2,14    {"operations": "300", "totaloperations": "301"},
        3,15    {"operations": "400", "totaloperations": "401"},
        4,16    {"operations": "500", "totaloperations": "501"},
        5,17    {"operations": "600", "totaloperations": "601"},
        6,18    {"operations": "700", "totaloperations": "701"},
        7,19    {"operations": "800", "totaloperations": "801"},
        ]
        """
        local_raw_responses = self.raw_responses.filter(path__slug=self.slugs[0])
        local_data = [raw_response.data for raw_response in local_raw_responses]
        [
            "environmental_impact_assessments",
            "public_disclosure", #? Where is public disclosure?
            "community_development_programs",
            "stakeholder_engagement_plans_",
            "local_community_consultation_committes",
            "works_councils,_occupational_health_and_safety_committees",
            "community_grievance_processes",
        ]
        for data in local_data:
            community_development = dict()
            total_operations = sum([int(item["totaloperations"]) for item in data])
            community_development["social_impact_assessments"] = safe_integer_divide(
                data[0]["operations"], total_operations
            )
            community_development["environmental_impact_assessments"] = (
                safe_integer_divide(data[1]["operations"], total_operations)
            )
            community_development["community_development_programs"] = (
                safe_integer_divide(data[3]["operations"], total_operations)
            )
            community_development["community_grievance_processes"] = (
                safe_integer_divide(data[7]["operations"], total_operations)
            )
            community_development["consultation_committees"] = safe_integer_divide(
                data[5]["operations"], total_operations
            )
            community_development["vulnerability_committees"] = safe_integer_divide(
                data[5]["operations"], total_operations
            )
            community_development["works_councils"] = safe_integer_divide(
                data[6]["operations"], total_operations
            )
            community_development["stakeholder_engagement_plans"] = safe_integer_divide(
                data[4]["operations"], total_operations
            )

    def get(self, request, format=None):
        """
        This function is used to get the social community development analysis.
        """
        serializer = CheckAnalysisViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.data["start"]
        self.end = serializer.data["end"]
        self.organisation = serializer.data.get("organisation")
        self.corporate = serializer.data.get("corporate")
        self.location = serializer.data.get("location")
        self.set_raw_responses()
