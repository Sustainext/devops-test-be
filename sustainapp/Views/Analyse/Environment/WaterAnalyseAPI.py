from datametric.models import RawResponse, DataPoint, Path, DataMetric
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    set_locations_data,
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
    get_location_wise_dictionary_data,
)
from collections import defaultdict
from django.db.models.expressions import RawSQL
from django.db.models import Q, Func, Value
import datetime
from common.utils.value_types import safe_divide, format_decimal_places


class WaterAnalyseByDataPoints(APIView):

    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri-environment-water-303-1b-1c-1d-interaction_with_water",
            1: "gri-environment-water-303-2a-management_water_discharge",
            2: "gri-environment-water-303-2a-profile_receiving_waterbody",
            3: "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas",
            4: "gri-environment-water-303-4a-third_party",
            5: "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress",
            6: "gri-environment-water-303-3b-water_withdrawal_areas_water_stress",
            7: "gri-environment-water-303-4d-substances_of_concern",
            8: "gri-environment-water-303-3d-4e-sma",
            9: "gri-environment-water-303-5c-change_in_water_storage",
            10: "gri-environment-water-303-5d-sma",
        }

    def get_total_water_consumption(self):
        slug = self.slugs[3]
        water_consumption_data = get_location_wise_dictionary_data(
            self.data_points.filter(path__slug=slug)
        )
        wa
        slug = self.slugs[5]
        water_consumption_data_with_water_stress_areas = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
        )
        water_consumption_total_consumption = []

    def calculate_total_withdrawal_discharge(self, data, withdrawal_key, discharge_key):
        """
        Calculate the total withdrawal and discharge for each location in the given data.

        Args:
            data (dict): A dictionary where keys are locations and values are lists of water data.

        Returns:
            dict: A dictionary with locations as keys and their total withdrawal and discharge as values.
        """
        summary = {}
        for location, records in data.items():
            total_withdrawal = 0
            total_discharge = 0

            for record in records:
                # Convert values to float to handle numerical calculations
                withdrawal = float(record[withdrawal_key])
                discharge = float(record[discharge_key])
                total_withdrawal += withdrawal
                total_discharge += discharge

            # Store the results in the summary dictionary
            summary[location] = {
                "total_consumption": total_withdrawal - total_discharge,
            }

        return summary

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

    def get(self, request, format=None):
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
        response_data = {}
        return Response(response_data, status=status.HTTP_200_OK)
