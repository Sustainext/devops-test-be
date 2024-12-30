from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from common.utils.value_types import safe_percentage, safe_divide


class TrainingAnalyzeAPI(APIView):
    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri-social-training_hours-404-1a-number_of_hours",
            1: "gri-social-performance_and_career-414-2b-number_of_suppliers",
            2: "gri-social-diversity_of_board-405-1b-number_of_employee",
        }

    def set_organized_data(self):
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0])
        )
        organized_data = [
            {
                "category": rw["category"],
                "number_of_male": int(rw["male1"]),
                "male_hrs": int(rw["male"]),
                "number_of_female": int(rw["female1"]),
                "female_hrs": int(rw["female"]),
                "number_of_others": int(rw["others1"]),
                "other_hrs": int(rw["others"]),
                "total_employees": int(rw["totalEmployees"]),
                "total_hrs": int(rw["totalTrainingHours"]),
            }
            for rw in raw_data
        ]
        return organized_data

    def get_total_employes_from_405_1b(self):
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[2])
        )
        # Process raw data for category and total employees
        data_list = [
            {
                "category": rw["category"],
                "total_employees": int(rw["totalGender"]),
            }
            for rw in raw_data
        ]

        # Process raw data for gender-specific employees
        genders_data = [
            {
                "male_employees": int(data.get("male", 0)),
                "female_employees": int(data.get("female", 0)),
                "other_employees": int(data.get("nonBinary", 0)),
            }
            for data in raw_data
        ]

        total_genders = {
            "Male": sum(data["male_employees"] for data in genders_data),
            "Female": sum(data["female_employees"] for data in genders_data),
            "Non-Binary": sum(data["other_employees"] for data in genders_data),
        }

        return data_list, total_genders

    def calculate_percentages(self, data, total_map, key_field):
        """Utility function to calculate performance and career development percentages."""
        result = []
        for item in data:
            key = item[key_field]
            if key in total_map:
                total_emp = total_map[key]
                result.append(
                    {
                        key_field: key,
                        "performance_percentage": safe_percentage(
                            item["performance"], total_emp
                        ),
                        "career_development_percentage": safe_percentage(
                            item["career_development"], total_emp
                        ),
                    }
                )
        return result

    def get_average_training_hours_provided_to_employess(self, organized_data):
        if not organized_data:
            return []
        average_hrs_of_training_provided_to_employees = safe_divide(
            sum(data["total_hrs"] for data in organized_data),
            sum(data["total_employees"] for data in organized_data),
        )
        average_training_hrs_per_female_employee = safe_divide(
            sum(data["female_hrs"] for data in organized_data),
            sum(data["number_of_female"] for data in organized_data),
        )
        average_training_hrs_per_male_employee = safe_divide(
            sum(data["male_hrs"] for data in organized_data),
            sum(data["number_of_male"] for data in organized_data),
        )

        result = [
            {
                "average_training_hours_per_employee": average_hrs_of_training_provided_to_employees,
                "average_training_hours_per_female_employee": average_training_hrs_per_female_employee,
                "average_training_hours_per_male_employee": average_training_hrs_per_male_employee,
            }
        ]

        return result

    def get_avg_hrs_by_category(self, organized_data):
        result = []
        for data in organized_data:
            result.append(
                {
                    "category": data["category"],
                    "avg_training_hrs_per_employee": safe_divide(
                        data["total_hrs"], data["total_employees"]
                    ),
                    "avg_training_hrs_male_employee": safe_divide(
                        data["male_hrs"], data["number_of_male"]
                    ),
                    "avg_training_hrs_female_employee": safe_divide(
                        data["female_hrs"], data["number_of_female"]
                    ),
                    "avg_training_hrs_other_employee": safe_divide(
                        data["other_hrs"], data["number_of_others"]
                    ),
                }
            )
        return result

    def get_percentage_of_employees(self):
        # Collect raw data
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[1])
        )

        # Retrieve total employees and gender data
        total_employees, total_genders = self.get_total_employes_from_405_1b()

        # Extract category data
        category_data = [
            {
                "category": rw.get("category"),
                "performance": int(rw.get("performance", 0)),
                "career_development": int(rw.get("careerDevelopment", 0)),
            }
            for rw in raw_data
            if rw.get("category") is not None
        ]

        # Extract gender data
        gender_data = [
            {
                "gender": rw.get("gender"),
                "performance": int(rw.get("performance1", 0)),
                "career_development": int(rw.get("careerDevelopment1", 0)),
            }
            for rw in raw_data
            if rw.get("gender") is not None
        ]

        # Calculate percentages for categories
        total_employees_map = {
            item["category"]: item["total_employees"] for item in total_employees
        }
        category_percentages = self.calculate_percentages(
            category_data, total_employees_map, "category"
        )

        # Calculate percentages for genders
        gender_percentages = self.calculate_percentages(
            gender_data, total_genders, "gender"
        )

        # Combine results
        return category_percentages + gender_percentages

    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(path__slug__in=list(self.slugs.values()))
            .filter(client_id=self.request.user.client.id)
            .filter(
                get_raw_response_filters(
                    corporate=self.corporate,
                    organisation=self.organisation,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        ).order_by("locale")

    def get(self, request, *args, **kwargs):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data.get("organisation")
        self.location = serializer.validated_data.get("location")  # * This is optional
        self.set_data_points()
        self.organized_data = self.set_organized_data()
        data = {}
        # * Table name: Average hours of training provided to employees
        data["average_hours_of_training_provided_to_employees"] = (
            self.get_average_training_hours_provided_to_employess(self.organized_data)
        )
        # * Table name: Average hours of training provided to employees per category
        data["average_hours_of_training_provided_to_employees_per_category"] = (
            self.get_avg_hrs_by_category(self.organized_data)
        )
        # * Table name: Percentage of employees receiving regular performance and career development reviews
        data[
            "percentage_of_employees_receiving_regular_performance_and_career_development_reviews"
        ] = self.get_percentage_of_employees()
        return Response(data, status=status.HTTP_200_OK)
