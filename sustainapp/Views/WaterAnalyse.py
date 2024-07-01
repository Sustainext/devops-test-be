"""
The WaterAnalyse class is an API view that provides functionality for analyzing water-related data.

The class has several methods that process and aggregate water data from various sources, including:
- Total water consumption in all areas and water stress areas
- Water consumption by business operation, location, source, and water type
- Water withdrawal from third parties
- Change in water storage

The class uses various helper methods to convert units, group and process the data, and calculate totals and percentages.

The get() method is the main entry point for the API, which takes query parameters to filter the data and returns a comprehensive response with various water-related metrics and statistics.
"""

from datametric.models import RawResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import set_locations_data
from collections import defaultdict


class WaterAnalyse(APIView):
    permission_classes = [IsAuthenticated]
    CONVERSION_FACTORS = {
        "litre": 1e-6,
        "cubic meter": 1e-3,
        "kilolitre": 1e-3,
        "million litres per day": 1,
        "megalitre": 1,
        "million litrse per day": 1,
    }
    discharge_literal = "Total Discharge"
    withdrawal_literal = "Total Withdrawal"
    consumed_literal = "Total Consumed"
    all_areas_slug = (
        "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas"
    )
    water_stress_area_slug = (
        "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress"
    )

    def set_raw_responses(self, slugs: list):
        self.raw_responses = RawResponse.objects.filter(
            year__range=(self.start.year, self.end.year),
            month__range=(self.start.month, self.end.month),
            path__slug__in=slugs,
            client=self.request.user.client,
            location__in=self.locations.values_list("name", flat=True),
        ).only("data", "location")

    def process_water_data(self, data, group_by_key, discharge_key, withdrawal_key):
        discharge_literal = self.discharge_literal
        withdrawal_literal = self.withdrawal_literal
        consumed_literal = self.consumed_literal
        grouped_data = defaultdict(
            lambda: {
                discharge_literal: 0,
                withdrawal_literal: 0,
                consumed_literal: 0,
                "Units": "",
            }
        )

        group_by_keys = (
            group_by_key if isinstance(group_by_key, list) else [group_by_key]
        )
        # Iterate over each entry in the data
        for entry in data:
            # Convert values to liters
            discharge = self.convert_to_megalitres(entry[discharge_key], entry["Unit"])
            withdrawal = self.convert_to_megalitres(
                entry[withdrawal_key], entry["Unit"]
            )
            consumed = discharge - withdrawal

            # Add the consumed water to the entry
            entry["Consumed"] = consumed
            group_key = tuple(entry[key] for key in group_by_keys)
            # Add the entry to the appropriate group
            grouped_data[group_key][discharge_literal] += discharge
            grouped_data[group_key][withdrawal_literal] += withdrawal
            grouped_data[group_key][consumed_literal] += consumed
            grouped_data[group_key]["Units"] = "KiloLitre"
            grouped_data[group_key]["Watertype"] = (
                entry["Watertype"] if "Watertype" in entry else ""
            )
            grouped_data[group_key]["Source"] = (
                entry["Source"] if "Source" in entry else ""
            )
            grouped_data[group_key]["waterstress"] = (
                entry["waterstress"] if "waterstress" in entry else ""
            )
        complete_total_consumption = sum(
            entry[consumed_literal] for entry in grouped_data.values()
        )
        complete_total_withdrawal = sum(
            entry[withdrawal_literal] for entry in grouped_data.values()
        )
        complete_total_discharge = sum(
            entry[discharge_literal] for entry in grouped_data.values()
        )
        result = []
        for group, data in grouped_data.items():
            total_discharge = data[discharge_literal]
            total_withdrawal = data[withdrawal_literal]
            total_consumed = data[consumed_literal]
            consumption_percentage = round(
                (
                    (total_consumed / complete_total_consumption) * 100
                    if complete_total_consumption != 0
                    else 0
                ),
                3,
            )
            withdrawal_percentage = round(
                (
                    (total_withdrawal / complete_total_withdrawal) * 100
                    if complete_total_withdrawal != 0
                    else 0
                ),
                3,
            )
            discharge_percentage = round(
                (
                    (total_discharge / complete_total_discharge) * 100
                    if complete_total_consumption != 0
                    else 0
                ),
                3,
            )
            group_dict = {group_by_keys[i]: group[i] for i in range(len(group_by_keys))}
            group_dict.update(
                {
                    self.discharge_literal: total_discharge,
                    self.withdrawal_literal: total_withdrawal,
                    "total_consumed": total_consumed,
                    "consumption_percentage": consumption_percentage,
                    "withdrawal_percentage": withdrawal_percentage,
                    "discharge_percentage": discharge_percentage,
                    "Units": data["Units"],
                    "WaterType": data["Watertype"],
                    "Source": data["Source"],
                    "WaterStress": data["waterstress"],
                }
            )
            result.append(group_dict)

        return result

    def process_third_party_water_data(
        self, data, group_by_key, discharge_key, withdrawal_key
    ):
        withdrawal_literal = withdrawal_key
        grouped_data = defaultdict(
            lambda: {
                withdrawal_literal: 0,
                "Units": "",
            }
        )
        if not isinstance(group_by_key, list):
            group_by_keys = [group_by_key]
        else:
            group_by_keys = group_by_key
        # Iterate over each entry in the data
        for entry in data:
            # Convert values to liters
            withdrawal = self.convert_to_megalitres(
                entry[withdrawal_key], entry["Unit"]
            )

            # Add the consumed water to the entry
            group_key = tuple(entry[key] for key in group_by_keys)
            # Add the entry to the appropriate group
            grouped_data[group_key][withdrawal_literal] += withdrawal
            grouped_data[group_key]["Units"] = "KiloLitre"
            grouped_data[group_key]["Source"] = (
                entry["Source"] if "Source" in entry else ""
            )
        complete_total_withdrawal = sum(
            entry[withdrawal_literal] for entry in grouped_data.values()
        )
        result = []
        for group, data in grouped_data.items():
            total_withdrawal = data[withdrawal_literal]
            withdrawal_percentage = round(
                (
                    (total_withdrawal / complete_total_withdrawal) * 100
                    if complete_total_withdrawal != 0
                    else 0
                ),
                3,
            )
            group_dict = {group_by_keys[i]: group[i] for i in range(len(group_by_keys))}
            group_dict.update(
                {
                    self.discharge_literal: total_withdrawal,
                    "Withdrawal Percentage": withdrawal_percentage,
                    "Units": data["Units"],
                }
            )
            result.append(group_dict)

        return result

    def process_third_party_discharge(self, data, group_by_key, discharge_key):
        discharge_literal = discharge_key
        grouped_data = defaultdict(
            lambda: {
                discharge_literal: 0,
                "Units": "",
            }
        )
        if not isinstance(group_by_key, list):
            group_by_keys = [group_by_key]
        else:
            group_by_keys = group_by_key
        # Iterate over each entry in the data
        for entry in data:
            # Convert values to liters
            discharge = self.convert_to_megalitres(entry[discharge_key], entry["Unit"])

            # Add the consumed water to the entry
            group_key = tuple(entry[key] for key in group_by_keys)
            # Add the entry to the appropriate group
            grouped_data[group_key][discharge_literal] += discharge
            grouped_data[group_key]["Units"] = "KiloLitre"
            grouped_data[group_key]["Source"] = (
                entry["Source"] if "Source" in entry else ""
            )
        complete_total_discharge = sum(
            entry[discharge_literal] for entry in grouped_data.values()
        )
        result = []
        for group, data in grouped_data.items():
            total_discharge = data[discharge_literal]
            discharge_percentage = round(
                (
                    (total_discharge / complete_total_discharge) * 100
                    if complete_total_discharge != 0
                    else 0
                ),
                3,
            )
            group_dict = {group_by_keys[i]: group[i] for i in range(len(group_by_keys))}
            group_dict.update(
                {
                    self.discharge_literal: total_discharge,
                    "Discharge Percentage": discharge_percentage,
                    "Units": data["Units"],
                }
            )
            result.append(group_dict)

        return result

    def convert_to_megalitres(self, value, unit):
        value = float(value)
        unit = unit.lower()
        if unit in self.CONVERSION_FACTORS:
            return value * self.CONVERSION_FACTORS[unit]
        else:
            raise ValidationError(f"Unknown unit: {unit}")

    def get_third_party_discharge_sent_to_use_other_organisations(self):
        local_raw_responses = self.raw_responses.filter(
            path__slug="gri-environment-water-303-4a-third_party"
        )
        data = []
        for raw_response in local_raw_responses:
            data.extend(raw_response.data)
        return self.process_third_party_discharge(
            data=data,
            group_by_key="Volume",
            discharge_key="Volume",
        )

    def process_change_in_water_storage(self, data):
        result = []
        processed_data = {
            "WaterStorage": 0,
        }
        for entry in data:
            processed_data["WaterStorage"] = self.convert_to_megalitres(
                value=float(entry["Reporting2"]) - float(entry["Reporting1"]),
                unit=entry["Unit"],
            )
            processed_data["Unit"] = "KiloLitre"
            result.append(processed_data)
        # * Sort the result by Water Storage
        result.sort(key=lambda x: x["WaterStorage"], reverse=True)
        return result

    def get_total_water_consumption_in_water_stress_areas(self):
        raw_responses = self.raw_responses.filter(
            path__slug=self.water_stress_area_slug
        )
        data = []
        for raw_response in raw_responses:
            data.extend(raw_response.data[0]["formData"])

        # Total Water Consumption in water stress areas
        by_water_consumption = self.process_water_data(
            data=data,
            group_by_key="Consumed",
            discharge_key="Waterdischarge",
            withdrawal_key="Waterwithdrawal",
        )

        # Total Fresh Water withdrawal by source (from water stress area)
        by_water_source = self.process_water_data(
            data=data,
            group_by_key="Source",
            discharge_key="Waterdischarge",
            withdrawal_key="Waterwithdrawal",
        )

        # Total Water withdrawal by Water type
        by_water_type = self.process_water_data(
            data=data,
            group_by_key="Watertype",
            discharge_key="Waterdischarge",
            withdrawal_key="Waterwithdrawal",
        )

        by_business_operation = self.process_water_data(
            data=data,
            group_by_key="Businessoperations",
            discharge_key="Waterdischarge",
            withdrawal_key="Waterwithdrawal",
        )
        return (
            by_water_consumption,
            by_water_source,
            by_water_type,
            by_business_operation,
        )

    def get_total_water_consumption_in_all_areas(self):
        raw_responses = self.raw_responses.filter(path__slug=self.all_areas_slug)
        data = []
        for raw_response in raw_responses:
            data.extend(raw_response.data)

        by_consumption = self.process_water_data(
            data=data,
            group_by_key="Consumed",
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        # * Total Water Consumption by business operation
        by_business_operation = self.process_water_data(
            data=data,
            group_by_key="Businessoperations",
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        # * Total Water Consumption by source
        by_source = self.process_water_data(
            data=data,
            group_by_key="Source",
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        # * Total Fresh Water withdrawal by business operation
        by_fresh_water = self.process_water_data(
            data=data,
            group_by_key="Businessoperations",
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        by_source_and_water_type = self.process_water_data(
            data=data,
            group_by_key=["Source", "Watertype"],
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        by_water_type = self.process_water_data(
            data=data,
            group_by_key="Watertype",
            discharge_key="discharge",
            withdrawal_key="withdrawal",
        )
        return (
            by_consumption,
            by_business_operation,
            by_source,
            by_fresh_water,
            by_source_and_water_type,
            by_water_type,
        )


    def calculate_totals_per_location(self, data):
        result = []
        overall_discharge = 0
        overall_withdrawal = 0
        overall_consumption = 0

        for location_dict in data:
            for location_name, records in location_dict.items():
                overall_discharge += sum(record["discharge"] for record in records)
                overall_withdrawal += sum(record["withdrawal"] for record in records)
                overall_consumption += sum(record["consumed"] for record in records)

        for location_dict in data:
            for location_name, records in location_dict.items():
                total_discharge = sum(record["discharge"] for record in records)
                total_withdrawal = sum(record["withdrawal"] for record in records)
                total_consumption = sum(record["consumed"] for record in records)

                discharge_contribution = (
                    (total_discharge / overall_discharge) * 100
                    if overall_discharge > 0
                    else 0
                )
                withdrawal_contribution = (
                    (total_withdrawal / overall_withdrawal) * 100
                    if overall_withdrawal > 0
                    else 0
                )
                consumption_contribution = (
                    (total_consumption / overall_consumption) * 100
                    if overall_consumption > 0
                    else 0
                )

                result.append(
                    {
                        "location": location_name,
                        "total_discharge": total_discharge,
                        "total_withdrawal": total_withdrawal,
                        "total_consumption": total_consumption,
                        "unit": "KiloLitre",
                        "discharge_contribution": discharge_contribution,
                        "withdrawal_contribution": withdrawal_contribution,
                        "consumption_contribution": consumption_contribution,
                    }
                )

        return result

    def process_water_data_by_location(self, data):

        for location_data in data:
            for location, entries in location_data.items():
                location_data[location] = list(
                    map(
                        lambda entry: {
                            "discharge": self.convert_to_megalitres(
                                entry["discharge"], entry["Unit"]
                            ),
                            "withdrawal": self.convert_to_megalitres(
                                entry["withdrawal"], entry["Unit"]
                            ),
                            "consumed": self.convert_to_megalitres(
                                entry["discharge"], entry["Unit"]
                            )
                            - self.convert_to_megalitres(
                                entry["withdrawal"], entry["Unit"]
                            ),
                            "total_discharge": entry.get("total_discharge", 0)
                            + self.convert_to_megalitres(
                                entry["discharge"], entry["Unit"]
                            ),
                            "total_withdrawal": entry.get("total_withdrawal", 0)
                            + self.convert_to_megalitres(
                                entry["withdrawal"], entry["Unit"]
                            ),
                            "total_consumed": entry.get("total_consumed", 0)
                            + (
                                self.convert_to_megalitres(
                                    entry["discharge"], entry["Unit"]
                                )
                                - self.convert_to_megalitres(
                                    entry["withdrawal"], entry["Unit"]
                                )
                            ),
                        },
                        entries,
                    )
                )
        return self.calculate_totals_per_location(data)

    def get_water_withdrawal_from_third_parties(self):
        local_raw_responses = self.raw_responses.filter(
            path__slug="gri-environment-water-303-3b-water_withdrawal_areas_water_stress"
        )
        data = []
        for raw_response in local_raw_responses:
            data.extend(raw_response.data)

        return self.process_third_party_water_data(
            data=data,
            group_by_key="Source",
            discharge_key="Waterdischarge",
            withdrawal_key="Quantity",
        )

    def get_by_location(self, slug):
        # * Filter Raw Responses by their location
        location_names = self.raw_responses.values_list(
            "location", flat=True
        ).distinct()
        data = []
        for location in location_names:
            local_raw_responses = (
                self.raw_responses.filter(location=location)
                .filter(path__slug=self.all_areas_slug)
                .only("data", "location")
            )
            for raw_response in local_raw_responses:
                data.append({location: raw_response.data})
        return self.process_water_data_by_location(data=data)

    def get_change_in_water_storage(self):
        slug = "gri-environment-water-303-5c-change_in_water_storage"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.extend(raw_response.data[0]["formData"])
        return self.process_change_in_water_storage(
            data,
        )

    def process_water_consumption_in_all_areas_and_stress_areas(
        self, all_areas_data, stress_areas_data
    ):
        return_data = []
        for all_area, stress_area in zip(all_areas_data, stress_areas_data):
            return_data.append(
                {
                    "Unit": "KiloLitre",
                    "total_water_consumption": self.convert_to_megalitres(
                        float(all_area["discharge"]) - float(all_area["withdrawal"]),
                        unit=all_area["Unit"],
                    ),
                    "water_consumption_from_areas_with_water_stress": self.convert_to_megalitres(
                        float(stress_area["Waterdischarge"])
                        - float(stress_area["Waterwithdrawal"]),
                        unit=stress_area["Unit"],
                    ),
                }
            )
        return return_data

    def get_water_consumption_in_all_areas_and_stress_areas(self):
        raw_responses = self.raw_responses.filter(path__slug=self.all_areas_slug)
        all_areas_data = []
        for raw_response in raw_responses:
            all_areas_data.extend(raw_response.data)
        raw_responses = self.raw_responses.filter(
            path__slug=self.water_stress_area_slug
        )
        water_stress_areas_data = []
        for raw_response in raw_responses:
            water_stress_areas_data.extend(raw_response.data[0]["formData"])
        return self.process_water_consumption_in_all_areas_and_stress_areas(
            all_areas_data=all_areas_data, stress_areas_data=water_stress_areas_data
        )

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data["organisation"]
        self.location = serializer.validated_data.get("location")  # * This is optional
        # * Set Locations Queryset
        self.locations = set_locations_data(
            organisation=self.organisation,
            corporate=self.corporate,
            location=self.location,
        )
        slugs = [
            "gri-environment-water-303-1b-1c-1d-interaction_with_water",
            "gri-environment-water-303-2a-management_water_discharge",
            "gri-environment-water-303-2a-profile_receiving_waterbody",
            self.all_areas_slug,
            "gri-environment-water-303-4a-third_party",
            self.water_stress_area_slug,
            "gri-environment-water-303-3b-water_withdrawal_areas_water_stress",
            "gri-environment-water-303-4d-substances_of_concern",
            "gri-environment-water-303-3d-4e-sma",
            "gri-environment-water-303-5c-change_in_water_storage",
            "gri-environment-water-303-5d-sma",
        ]
        self.set_raw_responses(slugs)
        (
            water_stress_by_water_consumption,
            water_stress_by_water_source,
            water_stress_by_water_type,
            water_stress_by_water_stress_business_operation,
        ) = self.get_total_water_consumption_in_water_stress_areas()

        (
            all_areas_by_consumption,
            all_areas_by_business_operation,
            all_areas_by_source,
            all_areas_by_fresh_water,
            all_areas_by_source_and_water_type,
            all_areas_by_water_type,
        ) = self.get_total_water_consumption_in_all_areas()

        response_data = {
            "total_water_consumption": self.get_water_consumption_in_all_areas_and_stress_areas(),
            "total_water_consumption_in_water_stress_areas": water_stress_by_water_consumption,
            "total_water_consumption_by_business_operation": all_areas_by_business_operation,
            "total_water_consumption_by_location": self.get_by_location(slug=None),
            "total_water_consumption_by_source": all_areas_by_source,
            "total_fresh_water_withdrawal_by_business_operation": all_areas_by_fresh_water,
            "total_fresh_water_withdrawal_by_source_from_water_stress_area": all_areas_by_source,
            "total_fresh_water_withdrawal_by_location_country": self.get_by_location(
                slug="gri-environment-water-303-3b-water_withdrawal_areas_water_stress"
            ),
            "total_water_withdrawal_by_water_type": all_areas_by_water_type,
            "water_withdrawal_from_third_parties": all_areas_by_source,
            "total_water_discharge_by_location": self.get_by_location("something"),
            "total_water_discharge_by_source_and_type_of_water": all_areas_by_source_and_water_type,
            "total_water_discharge_from_water_stress_area_by_business_operation": water_stress_by_water_stress_business_operation,
            "total_water_discharge_by_business_operation": all_areas_by_business_operation,
            "total_water_discharge_by_water_type_from_water_stress_area": water_stress_by_water_type,
            "third_party_water_discharge_sent_to_use_for_other_organizations": self.get_third_party_discharge_sent_to_use_other_organisations(),
            "change_in_water_storage": self.get_change_in_water_storage(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
