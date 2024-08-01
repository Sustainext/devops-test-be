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


class TrainingSocial(APIView):
    permission_classes = [IsAuthenticated]
    slugs = [
        "gri-social-training_hours-404-1a-number_of_hours",
        "gri-social-performance_and_career-414-2b-number_of_suppliers",
    ]

    def get_average_training_hours_per_employee_category(self, date_item_dict):
        temp_dict = {}
        for date_item in date_item_dict:
            temp_dict[
                "Average training hours per employee category: " + date_item["category"]
            ] = safe_integer_divide(
                date_item["totalEmployees"], date_item["totalTrainingHours"]
            )
        return temp_dict

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

    def get_average_training_hours(self):  # 404-1
        local_raw_responses = self.raw_responses.filter(path__slug=self.slugs[0])
        



    def get_employees_receiving_regular_updates(self):  # 404-3
        """
        Percentage of employees receiving regular performance and career development reviews
        """
        slug = self.slugs[1]
        local_raw_response = self.raw_responses.filter(path__slug=slug).first()


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
            "average_hours_of_training_provided_to_employees": self.get_average_training_hours(),
            "employees_receiving_regular_updates": self.get_employees_receiving_regular_updates(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
