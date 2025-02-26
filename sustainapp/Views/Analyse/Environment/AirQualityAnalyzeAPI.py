from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.views import APIView
from common.utils.value_types import safe_percentage
from datametric.models import DataPoint
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from rest_framework.response import Response
from rest_framework import status
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from collections import defaultdict


class AirQualityAnalyzeAPIView(APIView):
    def __init__(self):
        super().__init__()
        self.slugs = {0: "gri-environment-air-quality-nitrogen-oxide"}
        self.data_points = None
        self.start = None
        self.end = None
        self.organisation = None
        self.corporate = None
        self.location = None

    def set_data_points(self, request):
        """Fetch data points based on the request filters."""
        self.data_points = (
            DataPoint.objects.filter(path__slug__in=self.slugs.values())
            .filter(client_id=request.user.client.id)
            .filter(
                get_raw_response_filters(
                    corporate=self.corporate,
                    organisation=self.organisation,
                    location=self.location,
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
            .order_by("locale")
            .select_related("locale", "path")
        )

    def air_emission_by_pollution(self):
        """Compute air pollution emissions, grouping by pollutant and listing sources."""
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0])
        )

        if not raw_data:
            return []

        total_pollution = sum(float(data.get("Totalemissions", 0)) for data in raw_data)
        pollutant_data = defaultdict(
            lambda: {
                "total_emission": 0,
                "contribution": 0,
                "source_of_emission": set(),
            }
        )

        for data in raw_data:
            air_pollutant = data.get("AirPollutant")
            total_emission = float(data.get("Totalemissions", 0))
            source_of_emission = data.get("SourceofEmissionFactorused")

            if air_pollutant and source_of_emission:
                pollutant_data[air_pollutant]["total_emission"] += total_emission
                pollutant_data[air_pollutant]["source_of_emission"].add(
                    source_of_emission
                )
        result = [
            {
                "pollutant": pollutant,
                "total_emission": data["total_emission"],
                "contribution": safe_percentage(
                    data["total_emission"], total_pollution
                ),
                "source_of_emission": list(data["source_of_emission"]),
            }
            for pollutant, data in pollutant_data.items()
        ]

        result.append({"pollutant": "Total", "total_emission": total_pollution})
        return result

    def get(self, request, format=None):
        """API GET method to retrieve air quality analysis."""
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")

        self.set_data_points(request)

        response_data = {"air_emission_by_pollution": self.air_emission_by_pollution()}

        return Response(response_data, status=status.HTTP_200_OK)
