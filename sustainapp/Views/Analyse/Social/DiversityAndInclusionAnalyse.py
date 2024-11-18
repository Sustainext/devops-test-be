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
from datametric.models import RawResponse, DataPoint
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)


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
            .filter(year__range=(self.start.year, self.end.year))
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
            .prefetch_related("path")
            .order_by("-year", "-month")
        )

    def set_data_points(self):
        client_id = self.request.user.client.id
        self.data_points = (
            DataPoint.objects.filter(
                client_id=client_id,
                path__slug__in=self.slugs,
            )
            .filter(filter_by_start_end_dates(self.start, self.end))
            .filter(
                get_raw_response_filters(
                    organisation=self.organisation,
                    corporate=self.corporate,
                    location=self.location,
                )
            )
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
                    "percentage_of_employees_more_than_50_age_group": safe_divide(
                        int(category_data["moreThan50"]), int(category_data["totalAge"])
                    ),
                    "percentage_of_employees_in_minority_group": safe_divide(
                        int(category_data["minorityGroup"]),
                        int(category_data["vulnerableCommunities"]),
                    ),
                }
            )
        return local_response

    def get_diversity_of_the_individuals(self, slug):
        data_points = self.data_points.filter(path__slug=slug).order_by("index")
        data = collect_data_by_raw_response_and_index(data_points)
        calculate_dict = {}
        for item in data:
            for key, value in item.items():
                if key != "category":
                    if key in calculate_dict:
                        calculate_dict[key] += int(value)
                    else:
                        calculate_dict[key] = int(value)
        response_dict = {}
        
        # Calculating percentages
        if response_dict["totalGender"] > 0:
            response_dict["male_percentage"] = (
                response_dict["male"] / response_dict["totalGender"]
            ) * 100
            response_dict["female_percentage"] = (
                response_dict["female"] / response_dict["totalGender"]
            ) * 100
            response_dict["nonBinary_percentage"] = (
                response_dict["nonBinary"] / response_dict["totalGender"]
            ) * 100

        if response_dict["totalAge"] > 0:
            response_dict["lessThan30_percentage"] = (
                response_dict["lessThan30"] / response_dict["totalAge"]
            ) * 100
            response_dict["between30and50_percentage"] = (
                response_dict["between30and50"] / response_dict["totalAge"]
            ) * 100
            response_dict["moreThan50_percentage"] = (
                response_dict["moreThan50"] / response_dict["totalAge"]
            ) * 100

        # Calculating minority group percentage
        total_minority_and_vulnerable = (
            response_dict["minorityGroup"] + response_dict["vulnerableCommunities"]
        )
        if total_minority_and_vulnerable > 0:
            response_dict["minorityGroup_percentage"] = (
                response_dict["minorityGroup"] / total_minority_and_vulnerable
            ) * 100
            response_dict["vulnerableCommunities_percentage"] = (
                response_dict["vulnerableCommunities"] / total_minority_and_vulnerable
            ) * 100

        return response_dict

    def get_salary_ration(self, slug):  # 405-2
        local_raw_response = (
            self.raw_response.only("data").filter(path__slug=slug).first()
        )
        local_data = local_raw_response.data if local_raw_response is not None else []
        return local_data

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.set_raw_responses()
        self.set_data_points()
        response_data = {
            "percentage_of_employees_within_government_bodies": self.get_diversity_of_the_board(
                self.slugs[0]
            ),
            "number_of_employee_per_employee_category": self.get_diversity_of_the_board(
                self.slugs[1]
            ),
            "ratio_of_basic_salary_of_women_to_men": self.get_salary_ration(
                self.slugs[2]
            ),
            "ratio_of_remuneration_of_women_to_men": self.get_salary_ration(
                self.slugs[3]
            ),
            "diversity_of_the_individuals": self.get_diversity_of_the_individuals(
                self.slugs[0]
            ),
        }

        return Response(response_data, status=status.HTTP_200_OK)
