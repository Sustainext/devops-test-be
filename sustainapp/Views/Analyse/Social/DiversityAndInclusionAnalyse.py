from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datametric.utils.analyse import (
    set_locations_data,
    filter_by_start_end_dates,
    safe_divide,
)
from datametric.models import RawResponse


class DiversityAndInclusionAnalyse(APIView):
    permission_classes = [IsAuthenticated]

    slugs = [
        "gri-social-diversity_of_board-405-1a-number_of_individuals",
        "gri-social-diversity_of_board-405-1b-number_of_employee",
        "gri-social-salary_ratio-405-2a-number_of_individuals",
        "gri-social-salary_ratio-405-2a-ratio_of_remuneration",
    ]

    def set_raw_responses(self):
        user = self.request.user
        self.raw_response = (
            RawResponse.objects.filter(
                path__slug__in=self.slugs,
                client=user.client,
                locale__in=self.locations,
                user=user,
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .order_by("-year", "-month")
        )

    def get_diversity_of_the_board(self, slug):  # 405-1
        local_raw_response = (
            self.raw_response.only("data").filter(path__slug=slug).first()
        )
        local_data = local_raw_response.data
        local_response_dictionary = dict()
        for index, category_data in enumerate(local_data):
            local_response_dictionary[str(index) + category_data["category"]] = {
                "percentage_of_female_with_org_governance": safe_divide(
                    category_data["female"] / category_data["totalGender"]
                ),
                "percentage_of_male_with_org_governance": safe_divide(
                    category_data["male"] / category_data["totalGender"]
                ),
                "percentage_of_non_binary_with_org_governance": safe_divide(
                    category_data["nonBinary"] / category_data["totalGender"]
                ),
                "percentage_of_employees_within_30_age_group": safe_divide(
                    category_data["lessThan30"] / category_data["totalAge"]
                ),
                "percentage_of_employees_within_30_to_50_age_group": safe_divide(
                    category_data["between30and50"] / category_data["totalAge"]
                ),
                "percentage_of_employees_more than_50_age_group": safe_divide(
                    category_data["moreThan50"] / category_data["totalAge"]
                ),
                "percentage_of_employees_in_minority_group": safe_divide(
                    category_data["minorityGroup"]
                    / category_data["vulnerableCommunities"]
                ),
            }
        return local_response_dictionary

    def get_salary_ration(self, slug):  # 405-2
        local_raw_response = (
            self.raw_response.only("data").filter(path__slug=slug).first()
        )
        local_data = local_raw_response.data
        return local_data

    def post(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data["organisation"]
        corporate = serializer.validated_data.get("corporate")
        location = serializer.validated_data.get("location")
        self.locations = set_locations_data(
            organisation=organisation, corporate=corporate, location=location
        )
        self.set_raw_responses()
        response_data = {
            "percentage_of_employees_within_government_bodies": self.get_diversity_of_the_board(
                self.slugs[0]
            ),
            "number_of_employee_per_employee_category": self.get_diversity_of_the_board(
                self.slugs[1]
            ),
            "ratio-of-basic-salary-of-women-to-men": self.get_salary_ration(
                self.slugs[2]
            ),
            "ratio-of-remuneration-of-women-to-men": self.get_salary_ration(
                self.slugs[3]
            ),
        }

        return Response(response_data, status=status.HTTP_200_OK)
