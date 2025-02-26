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
from decimal import Decimal


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
        self.conversion_factors = {
            "Kilograms (kg)": Decimal(1),  # 1 kg = 1 kg
            "Pound (lb)": Decimal(0.45359237),  # 1 lb = 0.45359237 kg
            "ton (US short ton)": Decimal(907.18474),  # 1 US short ton = 907.18474 kg
            "Gram (g)": Decimal(0.001),  # 1 gram = 0.001 kg
            "tonnes (t)": Decimal(1000),  # 1 metric ton = 1000 kg
        }

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
        """Compute air pollution emissions, grouping by pollutant and listing sources, converting all units to kg.
        Also, store emissions in their original ppm or µg/m³ units where applicable.
        """
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0])
        )

        if not raw_data:
            return []

        total_pollution_kg = 0
        total_pollutant_ppm_or_ugm2 = 0
        pollutant_data_in_kg = defaultdict(
            lambda: {
                "total_emission_kg": 0,
                "contribution": 0,
                "source_of_emission": set(),
            }
        )

        pollutant_data_in_ppm_or_ugm2 = defaultdict(
            lambda: {
                "total_emission": 0,
                "unit": "",
                "source_of_emission": set(),
            }
        )

        for data in raw_data:
            emission_source = data.get("EmissionSource")
            air_pollutant = data.get("AirPollutant")
            total_emission = float(data.get("Totalemissions", 0))
            source_of_emission = data.get("SourceofEmissionFactorused")
            unit = data.get("Unit")

            key = (air_pollutant, emission_source)

            # If the unit is convertible to kg, process it in kg
            conversion_factor = self.conversion_factors.get(unit, None)
            if conversion_factor is not None:
                total_emission_kg = total_emission * float(conversion_factor)
                pollutant_data_in_kg[key]["total_emission_kg"] += total_emission_kg
                pollutant_data_in_kg[key]["source_of_emission"].add(source_of_emission)
                total_pollution_kg += total_emission_kg

            # If the unit is in ppm or µg/m³, store it separately
            else:
                pollutant_data_in_ppm_or_ugm2[key]["total_emission"] += total_emission
                pollutant_data_in_ppm_or_ugm2[key]["unit"] = unit
                pollutant_data_in_ppm_or_ugm2[key]["source_of_emission"].add(
                    source_of_emission
                )
                total_pollutant_ppm_or_ugm2 += total_emission

        # Construct result lists
        result_kg = [
            {
                "pollutant": pollutant[0],
                "total_emission_kg": data["total_emission_kg"],
                "contribution": safe_percentage(
                    data["total_emission_kg"], total_pollution_kg
                ),
                "source_of_emission": list(data["source_of_emission"]),
            }
            for pollutant, data in pollutant_data_in_kg.items()
        ]

        result_kg.append({"Total": total_pollution_kg})

        result_ppm_or_ugm2 = [
            {
                "pollutant": pollutant[0],
                "total_emission": data["total_emission"],
                "unit": data["unit"],
                "source_of_emission": list(data["source_of_emission"]),
            }
            for pollutant, data in pollutant_data_in_ppm_or_ugm2.items()
        ]
        result_ppm_or_ugm2.append(
            {
                "Total": total_pollutant_ppm_or_ugm2,
            }
        )

        return result_kg, result_ppm_or_ugm2

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
        air_emission_by_pollution, air_emission_by_pollution_ppm_or_ugm2 = (
            self.air_emission_by_pollution()
        )

        response_data = {
            "air_emission_by_pollution": air_emission_by_pollution,
            "air_emission_by_pollution_ppm_or_ugm2": air_emission_by_pollution_ppm_or_ugm2,
        }

        return Response(response_data, status=status.HTTP_200_OK)
