from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from datametric.models import RawResponse
from datametric.utils.analyse import (
    set_locations_data,
    filter_by_start_end_dates,
    safe_integer_divide,
    get_raw_response_filters,
    get_sum_from_dictionary_list,
)
from statistics import mean


class TrainingSocial(APIView):
    permission_classes = [IsAuthenticated]
    slugs = [
        "gri-social-training_hours-404-1a-number_of_hours",
        "gri-social-performance_and_career-414-2b-number_of_suppliers",
    ]

    def set_raw_responses(self):
        user = self.request.user

        self.raw_responses = (
            RawResponse.objects.filter(
                path__slug__in=self.slugs,
                client=user.client,
            )
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

    def get_average_training_hours_per_employee_category(self):  # 404-1a
        local_raw_responses = self.raw_responses.filter(path__slug=self.slugs[0])
        local_data = []
        for raw_response in local_raw_responses:
            local_data.extend(raw_response.data)

        categories = {}

        for item in local_data:
            category = item["category"]
            if category not in categories:
                categories[category] = []

            categories[category].append(
                {
                    "average_training_hours_per_employee": safe_integer_divide(
                        item["totalTrainingHours"], item["totalEmployees"]
                    ),
                    "average_training_hours_per_female_employee": safe_integer_divide(
                        item["female1"], item["female"]
                    ),
                    "average_training_hours_per_male_employee": safe_integer_divide(
                        item["male1"], item["male"]
                    ),
                    "average_training_hours_per_non_binary_employee": safe_integer_divide(
                        item["others1"], item["others"]
                    ),
                }
            )

        result = []
        for category, data_list in categories.items():
            result.append(
                {
                    "category": category,
                    "average_training_hours_per_employee": mean(
                        [
                            item["average_training_hours_per_employee"]
                            for item in data_list
                        ]
                    ),
                    "average_training_hours_per_female_employee": mean(
                        [
                            item["average_training_hours_per_female_employee"]
                            for item in data_list
                        ]
                    ),
                    "average_training_hours_per_male_employee": mean(
                        [
                            item["average_training_hours_per_male_employee"]
                            for item in data_list
                        ]
                    ),
                    "average_training_hours_per_non_binary_employee": mean(
                        item["average_training_hours_per_non_binary_employee"]
                        for item in data_list
                    ),
                }
            )

        return result

    def get_average_hours_of_training_provided_to_employees(self):  # 404-1
        """
        Response Example:

        """
        local_raw_responses = self.raw_responses.filter(path__slug=self.slugs[0])
        local_data = []
        local_response_data = []
        for raw_response in local_raw_responses:
            local_data.extend(raw_response.data)

        for local_data_item in local_data:
            local_response_data.append(
                {
                    "average_training_hours_per_employee": safe_integer_divide(
                        local_data_item[
                            "totalEmployees"
                        ],  # * This is wrong data metriced, this gives total working hours instead of total number of employees.
                        local_data_item["totalTrainingHours"],
                    ),
                    "average_training_hours_per_female_employee": safe_integer_divide(
                        local_data_item["female"], local_data_item["female1"]
                    ),
                    "average_training_hours_per_male_employee": safe_integer_divide(
                        local_data_item["male"], local_data_item["male1"]
                    ),
                    "average_training_hours_per_non_binary_employee": safe_integer_divide(
                        local_data_item["others"], local_data_item["others1"]
                    ),
                }
            )
        # * Get average of every item in response_data
        # * Get sum of Average training hours per employee.
        return [
            {
                "average_training_hours_per_employee": mean(
                    [
                        item["average_training_hours_per_employee"]
                        for item in local_response_data
                    ],
                ),
                "average_training_hours_per_female_employee": mean(
                    [
                        item["average_training_hours_per_female_employee"]
                        for item in local_response_data
                    ],
                ),
                "average_training_hours_per_male_employee": mean(
                    [
                        item["average_training_hours_per_male_employee"]
                        for item in local_response_data
                    ],
                ),
                "average_training_hours_per_non_binary_employee": mean(
                    [
                        item["average_training_hours_per_non_binary_employee"]
                        for item in local_response_data
                    ],
                ),
            },
        ]

    def get_percentage_of_employees_receiving_regular_performance_and_career_development_reviews(
        self,
    ):
        local_raw_response = self.raw_responses.filter(path__slug=self.slugs[1]).first()
        data = local_raw_response.data

        response_data = []
        for item in data:
            response_data.append(
                {
                    "Category": item["category"],
                    "percentage_of_employees_who_received_regular_performance_reviews": safe_integer_divide(
                        item["totalTrainingHours"], item["totalEmployees"]
                    ),
                    "percentage_of_employees_who_received_regular_career_development_reviews": safe_integer_divide(
                        item["totalEmployees"], item["totalEmployees"]
                    ),
                }
            )
        return response_data

    def get_percentage_of_employees_receiving_regular_performance_and_career_development_reviews_by_gender(
        self,
    ):
        local_raw_response = self.raw_responses.filter(path__slug=self.slugs[1]).first()
        data = local_raw_response.data

        total_employees = sum(int(item["totalEmployees"]) for item in data)

        genders = [
            ("Male", "male", "male1"),
            ("Female", "female", "female1"),
            ("Non-Binary", "others", "others1"),
        ]

        return [
            {
                "Gender": gender,
                "percentage_of_employees_who_received_regular_performance_reviews": safe_integer_divide(
                    sum(item[key1] for item in data), total_employees
                ),
                "percentage_of_employees_who_received_regular_career_development_reviews": safe_integer_divide(
                    sum(item[key2] for item in data), total_employees
                ),
            }
            for gender, key1, key2 in genders
        ]

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.set_raw_responses()
        response_data = {
            "average_hours_of_training_provided_to_employees": self.get_average_hours_of_training_provided_to_employees(),
            "average_training_hours_per_employee_category": self.get_average_training_hours_per_employee_category(),
            "percentage_of_employees_receiving_regular_performance_and_career_development_reviews": self.get_percentage_of_employees_receiving_regular_performance_and_career_development_reviews(),
            "percentage_of_employees_receiving_regular_performance_and_career_development_reviews_by_gender": self.get_percentage_of_employees_receiving_regular_performance_and_career_development_reviews_by_gender(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
