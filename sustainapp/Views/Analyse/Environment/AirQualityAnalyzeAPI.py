from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework.views import APIView
from common.utils.value_types import safe_percentage, format_decimal_places
from datametric.models import DataPoint
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from rest_framework.response import Response
from rest_framework import status
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
    get_location_wise_dictionary_data,
)
from collections import defaultdict
from decimal import Decimal
from sustainapp.Utilities.air_quality_analyze import ods_potential


class AirQualityAnalyzeAPIView(APIView):
    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri-environment-air-quality-nitrogen-oxide",
            1: "gri-environment-air-quality-emission-ods",
        }
        self.data_points = None
        self.data_points_for_location_wise = None
        self.start = None
        self.end = None
        self.organisation = None
        self.corporate = None
        self.location = None
        self.conversion_factors = {
            "Kilograms (kg)": Decimal(1),  # 1 kg = 1 kg
            "Pound (lb)": Decimal(0.45359237),  # 1 lb = 0.45359237 kg
            "ton (US Short ton)": Decimal(907.18474),  # 1 US short ton = 907.18474 kg
            "Gram (g)": Decimal(0.001),  # 1 gram = 0.001 kg
            "tonnes (t)": Decimal(1000),  # 1 metric ton = 1000 kg
        }
        self.conversion_factors_for_ods = {
            "Kilogram(Kg)": (0.001),  # 1 kg = 0.001 tons
            "Pound (lb)": (0.00045359237),  # 1 lb = 0.00045359237 tons
            "ton(US Short ton)": (0.90718474),  # 1 US Short ton = 0.90718474 tons
            "Gram(g)": (0.000001),  # 1 g = 0.000001 tons
            "Tons": (1),  # Already in tons, no change needed
        }
        self.ods_potential = ods_potential

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

    def set_data_points_for_location_table(self, request):
        """Fetch data points based on the request filters."""
        self.data_points_for_location_wise = (
            DataPoint.objects.filter(path__slug__in=self.slugs.values())
            .filter(client_id=request.user.client.id)
            .filter(
                get_raw_response_filters(
                    corporate=self.corporate_for_location,
                    organisation=self.organisation,
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
            return [], []

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
                pollutant_data_in_kg[key]["unit"] = unit
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

        result_kg = [
            {
                "SNO": index + 1,
                "pollutant": pollutant[0],
                "total_emission_kg": data["total_emission_kg"],
                "initial_unit": data["unit"],
                "converted_unit": "Kilograms (kg)",
                "contribution": safe_percentage(
                    data["total_emission_kg"], total_pollution_kg
                ),
                "source_of_emission": list(data["source_of_emission"]),
            }
            for index, (pollutant, data) in enumerate(pollutant_data_in_kg.items())
        ]
        result_kg.append({"Total": total_pollution_kg})

        result_ppm_or_ugm2 = [
            {
                "SNO": index + 1,
                "pollutant": pollutant[0],
                "total_emission": data["total_emission"],
                "unit": data["unit"],
                "source_of_emission": list(data["source_of_emission"]),
            }
            for index, (pollutant, data) in enumerate(
                pollutant_data_in_ppm_or_ugm2.items()
            )
        ]
        result_ppm_or_ugm2.append(
            {
                "Total": total_pollutant_ppm_or_ugm2,
            }
        )

        return result_kg, result_ppm_or_ugm2

    def percentage_contribution_of_pollutant_by_location(self):
        """Compute the percentage contribution of each pollutant by location (including user-added pollutants)."""

        required_pollutants = [
            "NOx",
            "SOx",
            "Persistent organic pollutants (POP)",
            "Volatile organic compounds (VOC)",
            "Hazardous air pollutants (HAP)",
            "Particulate matter (PM 10)",
            "Particulate matter (PM 2.5)",
            "Carbon Monoxide(CO)",
        ]

        raw_data = get_location_wise_dictionary_data(
            self.data_points_for_location_wise.filter(path__slug=self.slugs[0])
        )

        locations = list(raw_data.keys())

        total_emissions_per_pollutant_kg = defaultdict(float)

        structured_data = defaultdict(lambda: {"location": ""})

        all_pollutants = set(required_pollutants)

        for location in locations:
            structured_data[location]["location"] = location

            location_data = raw_data[location]
            for entry in location_data:
                pollutant = entry["AirPollutant"]
                emission_value = Decimal(entry["Totalemissions"])
                unit = entry["Unit"]

                all_pollutants.add(pollutant)

                conversion_factor = self.conversion_factors.get(unit, None)
                if conversion_factor is not None:
                    emission_value_kg = emission_value * conversion_factor

                    total_emissions_per_pollutant_kg[pollutant] += float(
                        emission_value_kg
                    )

                    if pollutant in structured_data[location]:
                        structured_data[location][pollutant] += float(emission_value_kg)
                    else:
                        structured_data[location][pollutant] = float(emission_value_kg)

        for location in locations:
            for pollutant in all_pollutants:
                total_emission_kg = total_emissions_per_pollutant_kg.get(pollutant, 0)

                if pollutant in structured_data[location]:
                    location_emission_kg = structured_data[location][pollutant]
                    structured_data[location][pollutant] = safe_percentage(
                        location_emission_kg, total_emission_kg
                    )
                else:
                    structured_data[location][pollutant] = "0.00"

        final_data = list(structured_data.values())
        for index, item in enumerate(final_data, start=1):
            item_with_sno_first = {"SNO": index, **item}
            final_data[index - 1] = item_with_sno_first

        if self.location:
            filtered_data = [
                item for item in final_data if item["location"] == self.location.name
            ]

            # Reassign SNO after filtering
            for new_index, item in enumerate(filtered_data, start=1):
                item["SNO"] = new_index

            return filtered_data if filtered_data else []

        return final_data

    def total_air_pollution_by_location(self):
        """Compute the total air pollution by location (including user-added pollutants)."""

        required_pollutants = [
            "NOx",
            "SOx",
            "Persistent organic pollutants (POP)",
            "Volatile organic compounds (VOC)",
            "Hazardous air pollutants (HAP)",
            "Particulate matter (PM 10)",
            "Particulate matter (PM 2.5)",
            "Carbon Monoxide(CO)",
        ]

        raw_data = get_location_wise_dictionary_data(
            self.data_points_for_location_wise.filter(path__slug=self.slugs[0])
        )
        if not raw_data:
            return [], []

        locations = list(raw_data.keys())

        total_emissions_per_location_kg = defaultdict(float)
        structured_data_kg = defaultdict(lambda: {"location": ""})
        structured_data_ppm_or_ugm2 = defaultdict(lambda: {"location": ""})

        all_pollutants = set(required_pollutants)

        for location in locations:
            structured_data_kg[location]["location"] = location
            structured_data_ppm_or_ugm2[location]["location"] = location

            location_data = raw_data[location]
            for entry in location_data:
                pollutant = entry["AirPollutant"]
                emission_value = Decimal(entry["Totalemissions"])
                unit = entry["Unit"]

                all_pollutants.add(pollutant)

                conversion_factor = self.conversion_factors.get(unit, None)
                if conversion_factor is not None:
                    emission_value_kg = emission_value * conversion_factor

                    total_emissions_per_location_kg[pollutant] += float(
                        emission_value_kg
                    )

                    structured_data_kg[location][pollutant] = structured_data_kg[
                        location
                    ].get(pollutant, 0) + float(emission_value_kg)

                else:
                    structured_data_ppm_or_ugm2[location][pollutant] = (
                        structured_data_ppm_or_ugm2[location].get(pollutant, 0)
                        + float(emission_value)
                    )

        for location in locations:
            for pollutant in all_pollutants:
                structured_data_kg[location].setdefault(pollutant, 0)
                structured_data_ppm_or_ugm2[location].setdefault(pollutant, 0)

        structured_data_kg_filtered = [
            data
            for data in structured_data_kg.values()
            if any(value != 0 for key, value in data.items() if key != "location")
        ]
        structured_data_ppm_or_ugm2_filtered = [
            data
            for data in structured_data_ppm_or_ugm2.values()
            if any(value != 0 for key, value in data.items() if key != "location")
        ]

        for index, item in enumerate(structured_data_kg_filtered, start=1):
            item_with_sno_first = {"SNO": index, **item}
            structured_data_kg_filtered[index - 1] = item_with_sno_first

        for index, item in enumerate(structured_data_ppm_or_ugm2_filtered, start=1):
            item_with_sno_first = {"SNO": index, **item}
            structured_data_ppm_or_ugm2_filtered[index - 1] = item_with_sno_first

        # Calculate total for each pollutant
        total_kg = {"location": "Total"}
        for pollutant in all_pollutants:
            total_kg[pollutant] = sum(
                item.get(pollutant, 0) for item in structured_data_kg_filtered
            )

        total_ppm_or_ugm2 = {
            "location": "Total",
        }
        for pollutant in all_pollutants:
            total_ppm_or_ugm2[pollutant] = sum(
                item.get(pollutant, 0) for item in structured_data_ppm_or_ugm2_filtered
            )

        if any(
            value != 0
            for key, value in total_kg.items()
            if key not in ["SNO", "location"]
        ):
            structured_data_kg_filtered.append(total_kg)

        if any(
            value != 0
            for key, value in total_ppm_or_ugm2.items()
            if key not in ["SNO", "location"]
        ):
            structured_data_ppm_or_ugm2_filtered.append(total_ppm_or_ugm2)

        return (
            structured_data_kg_filtered or [],
            structured_data_ppm_or_ugm2_filtered or [],
        )

    def ozone_depleting_substances(self):
        """Compute ozone-depleting substances in tons."""
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points_for_location_wise.filter(path__slug=self.slugs[1])
        )

        if not raw_data:
            return []

        result = {}

        for data in raw_data:
            source = data.get("EmissionSource", "")
            ods = data.get("ODS", "")

            # Extract values, defaulting to 0 if missing
            ods_produced = float(data.get("ODSProduced", 0) or 0)
            ods_destroyed_by_approved_techniques = float(
                data.get("ODSDestroyedbyapprovedtechnologies", 0) or 0
            )
            ods_as_feedback = float(data.get("ODSUsedasfeedstock", 0) or 0)
            ods_imported = float(data.get("ODSImported", 0) or 0)
            ods_exported = float(data.get("ODSExported", 0) or 0)
            unit = data.get("Unit", "")

            key = (source, ods)

            conversion_factor = self.conversion_factors_for_ods.get(unit, None)

            if conversion_factor is not None:
                # Convert to tons (Now both are Decimals, avoiding TypeError)
                ods_produced_ton = ods_produced * conversion_factor
                ods_destroyed_by_approved_techniques_ton = (
                    ods_destroyed_by_approved_techniques * conversion_factor
                )
                ods_as_feedback_ton = ods_as_feedback * conversion_factor
                ods_imported_ton = ods_imported * conversion_factor
                ods_exported_ton = ods_exported * conversion_factor

                if key not in result:
                    result[key] = {
                        "source": source,
                        "ods": ods,
                        "total_ods_produced_ton": 0,
                        "total_ods_destroyed_by_approved_techniques_ton": 0,
                        "total_ods_as_feedback_ton": 0,
                        "total_ods_imported_ton": 0,
                        "total_ods_exported_ton": 0,
                    }

                # Accumulate values
                result[key]["total_ods_produced_ton"] += ods_produced_ton
                result[key]["total_ods_destroyed_by_approved_techniques_ton"] += (
                    ods_destroyed_by_approved_techniques_ton
                )
                result[key]["total_ods_as_feedback_ton"] += ods_as_feedback_ton
                result[key]["total_ods_imported_ton"] += ods_imported_ton
                result[key]["total_ods_exported_ton"] += ods_exported_ton

        total_net_ods_emitted = sum(
            (
                (values["total_ods_produced_ton"] + values["total_ods_imported_ton"])
                - (
                    values["total_ods_destroyed_by_approved_techniques_ton"]
                    + values["total_ods_as_feedback_ton"]
                    + values["total_ods_exported_ton"]
                )
            )
            * self.ods_potential.get(values["ods"], 0)
            for values in result.values()
        )

        final_data = []

        for index, (key, values) in enumerate(result.items(), start=1):
            ods_name = values["ods"]
            net_ods_production_ton = (
                values["total_ods_produced_ton"]
                - values["total_ods_destroyed_by_approved_techniques_ton"]
                - values["total_ods_as_feedback_ton"]
            )
            net_ods_emitted = (
                values["total_ods_produced_ton"] + values["total_ods_imported_ton"]
            ) - (
                values["total_ods_destroyed_by_approved_techniques_ton"]
                + values["total_ods_as_feedback_ton"]
                + values["total_ods_exported_ton"]
            )
            ods_value = self.ods_potential.get(ods_name, 0)
            net_ods_emitted_with_ods = net_ods_emitted * ods_value

            contribution = (
                (net_ods_emitted_with_ods / total_net_ods_emitted * 100)
                if total_net_ods_emitted != 0
                else 0
            )

            final_data.append(
                {
                    "SNO": index,
                    "source": values["source"],
                    "ods": values["ods"],
                    "net_ods_emitted": format_decimal_places(net_ods_emitted_with_ods),
                    "contribution_percentage": format_decimal_places(contribution),
                    "net_ods_production_ton": format_decimal_places(
                        net_ods_production_ton
                    ),
                    "total_ods_imported_ton": format_decimal_places(
                        values["total_ods_imported_ton"]
                    ),
                    "total_ods_exported_ton": format_decimal_places(
                        values["total_ods_exported_ton"]
                    ),
                    "source_of_emission_factor": "Montreal Protocol",
                }
            )
        final_data.append(
            {
                "total_net_ods_emitted": format_decimal_places(total_net_ods_emitted),
            }
        )

        return final_data

    def get(self, request, format=None):
        """API GET method to retrieve air quality analysis."""
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.organisation = serializer.validated_data.get("organisation")
        self.corporate = serializer.validated_data.get("corporate")
        self.location = serializer.validated_data.get("location")
        self.corporate_for_location = self.corporate
        if self.location:
            self.corporate_for_location = self.location.corporateentity

        self.set_data_points(request)
        self.set_data_points_for_location_table(request)
        air_emission_by_pollution, air_emission_by_pollution_ppm_or_ugm2 = (
            self.air_emission_by_pollution()
        )
        percentage_contribution_of_pollutant_by_location = (
            self.percentage_contribution_of_pollutant_by_location()
        )
        (
            total_air_pollution_by_location_kg,
            total_air_pollution_by_location_ppm_or_ugm2,
        ) = self.total_air_pollution_by_location()

        ozone_depleting_substances = self.ozone_depleting_substances()

        response_data = {
            "air_emission_by_pollution": air_emission_by_pollution,
            "air_emission_by_pollution_ppm_or_ugm2": air_emission_by_pollution_ppm_or_ugm2,
            "percentage_contribution_of_pollutant_by_location": percentage_contribution_of_pollutant_by_location,
            "total_air_pollution_by_location": total_air_pollution_by_location_kg,
            "total_air_pollution_by_location_ppm_or_ugm2": total_air_pollution_by_location_ppm_or_ugm2,
            "ozone_depleting_substances": ozone_depleting_substances,
        }

        return Response(response_data, status=status.HTTP_200_OK)
