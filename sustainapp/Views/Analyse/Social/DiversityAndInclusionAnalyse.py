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
    get_raw_response_filters,
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
            )
            .get_raw_response_filters()
            .filter(year__range=(self.start.year, self.end.year))
            .order_by("-year", "-month")
        )

    def get_diversity_of_the_board(self, slug):  # 405-1
        local_raw_response = (
            self.raw_response.only("data").filter(path__slug=slug).first()
        )
        local_data = local_raw_response.data if local_raw_response is not None else []
        local_response = list()
        for category_data in local_data:
            local_response.append(
                {
                    "Category": category_data["category"],
                    "percentage_of_female_with_org_governance": safe_divide(
                        int(category_data["female"]), int(category_data["totalGender"])
                    ),
                    "percentage_of_male_with_org_governance": safe_divide(
                        int(category_data["male"]), int(category_data["totalGender"])
                    ),
                    "percentage_of_non_binary_with_org_governance": safe_divide(
                        int(category_data["nonBinary"]),
                        int(category_data["totalGender"]),
                    ),
                    "percentage_of_employees_within_30_age_group": safe_divide(
                        int(category_data["lessThan30"]), int(category_data["totalAge"])
                    ),
                    "percentage_of_employees_within_30_to_50_age_group": safe_divide(
                        int(category_data["between30and50"]),
                        int(category_data["totalAge"]),
                    ),
                    "percentage_of_employees_more than_50_age_group": safe_divide(
                        int(category_data["moreThan50"]), int(category_data["totalAge"])
                    ),
                    "percentage_of_employees_in_minority_group": safe_divide(
                        int(category_data["minorityGroup"]),
                        int(category_data["vulnerableCommunities"]),
                    ),
                }
            )
        return local_response

    def get_salary_ration(self, slug):  # 405-2
        local_raw_response = (
            self.raw_response.only("data").filter(path__slug=slug).first()
        )
        local_data = local_raw_response.data if local_raw_response is not None else []
        return local_data

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data["organisation"]
        corporate = serializer.validated_data.get("corporate")
        location = serializer.validated_data.get("location")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
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
