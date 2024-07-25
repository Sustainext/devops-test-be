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
        local_data = []
        for local_raw_response in local_raw_responses:
            local_data.append(local_raw_response.data)
        # * local_data contains list of data for each month of each year.
        local_response_data = []
        for each_date_item in local_data:
            for each_category_data in each_date_item:
                temp_dict = {}
                temp_dict["Average training hours per employee"] = safe_integer_divide(
                    each_category_data["totalEmployees"],
                    each_category_data["totalTrainingHours"],
                )
                temp_dict["Average training hours per Female employee"] = (
                    safe_integer_divide(
                        each_category_data["female"],
                        each_category_data["female1"],
                    )
                )
                temp_dict["Average training hours per Male employee"] = (
                    safe_integer_divide(
                        each_category_data["male"],
                        each_category_data["male1"],
                    )
                )
                temp_dict["Average training hours per employee category"] = (
                    safe_integer_divide(
                        each_category_data["totalEmployees"],
                        each_category_data["totalTrainingHours"],
                    )
                )
                local_response_data.append(temp_dict)
        return local_response_data

    def get_employees_receiving_regular_updates(self):  # 404-3
        """
        Percentage of employees receiving regular performance and career development reviews
        """
        slug = self.slugs[1]
        local_raw_response = self.raw_responses.filter(path__slug=slug).first()
        local_data = local_raw_response.data if local_raw_response is not None else []
        """
        *Response Format
        [
            {
            "category": 'Percentage of employees who received regular performance review',
            "a": '',
            "b": '',
            "male": '',
            "female": '',
            "nonBinary": '',
            },
            {
            "category": 'Percentage of employees who received regular career development review',
            "a": '',
            "b": '',
            "male": '',
            "female": '',
            "nonBinary": '',
            },
        ]
        """
        local_response_data = [
            {
                "category": "Percentage of employees who received regular performance review",
                "a": safe_integer_divide(
                    local_data[0]["male"]
                    + local_data[0]["female"]
                    + local_data[0]["nonBinary"],
                    local_data[0]["totalTrainingHours"],
                ),
                "b": safe_integer_divide(
                    local_data[0]["male2"]
                    + local_data[0]["female2"]
                    + local_data[0]["nonBinary2"],
                    local_data[0]["totalTrainingHours2"],
                ),
                "female": safe_integer_divide(
                    local_data[0]["female"],
                    local_data[0]["totalTrainingHours"],
                ),
                "male": safe_integer_divide(
                    local_data[0]["male"],
                    local_data[0]["totalTrainingHours"],
                ),
                "nonBinary": safe_integer_divide(
                    local_data[0]["nonBinary"],
                    local_data[0]["totalTrainingHours"],
                ),
            },
            {
                "category": "Percentage of employees who received regular career development review",
                "a": safe_integer_divide(
                    local_data[0]["male"]
                    + local_data[0]["female"]
                    + local_data[0]["nonBinary"],
                    local_data[0]["totalTrainingHours"],
                ),
                "b": safe_integer_divide(
                    local_data[0]["male2"]
                    + local_data[0]["female2"]
                    + local_data[0]["nonBinary2"],
                    local_data[0]["totalTrainingHours2"],
                ),
                "female": safe_integer_divide(
                    local_data[0]["female2"],
                    local_data[0]["totalTrainingHours2"],
                ),
                "male": safe_integer_divide(
                    local_data[0]["male2"],
                    local_data[0]["totalTrainingHours2"],
                ),
                "nonBinary": safe_integer_divide(
                    local_data[0]["nonBinary2"],
                    local_data[0]["totalTrainingHours2"],
                ),
            },
        ]
        return local_response_data

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
