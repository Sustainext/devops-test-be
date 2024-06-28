from datametric.models import DataPoint, Path, RawResponse
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
        if not isinstance(group_by_key, list):
            group_by_keys = [group_by_key]
        else:
            group_by_keys = group_by_key
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
                    "Total Discharge": total_discharge,
                    "Total Withdrawal": total_withdrawal,
                    "Total Consumed": total_consumed,
                    "Consumption Percentage": consumption_percentage,
                    "Withdrawal Percentage": withdrawal_percentage,
                    "Discharge Percentage": discharge_percentage,
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
                    "Total Withdrawal": total_withdrawal,
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
                    "Total Discharge": total_discharge,
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
            path__slug="gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress"
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

        # ? Total Fresh Water withdrawal by Location/Country

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
        raw_responses = self.raw_responses.filter(
            path__slug="gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas"
        )
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
        return (
            by_consumption,
            by_business_operation,
            by_source,
            by_fresh_water,
            by_source_and_water_type,
        )

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
        # TODO: Make it dynamic, instead of static.
        water_discharge_data = {
            "Location 1": {
                "Discharge Percentage": "x%",
                "Total Discharge": "212123545",
                "Total Withdrawal": "212123545",
                "Total Consumed": "212123545",
                "Units": "Megalitre",
            },
            "Location 2": {
                "Discharge Percentage": "x%",
                "Total Discharge": "212123545",
                "Total Withdrawal": "212123545",
                "Total Consumed": "212123545",
                "Units": "Megalitre",
            },
            "Location 3": {
                "Discharge Percentage": "x%",
                "Total Discharge": "212123545",
                "Total Withdrawal": "212123545",
                "Total Consumed": "212123545",
                "Units": "Megalitre",
            },
        }

        return water_discharge_data

    def get_change_in_water_storage(self):
        slug = "gri-environment-water-303-5c-change_in_water_storage"
        local_raw_response = self.raw_responses.filter(path__slug=slug)
        data = []
        for raw_response in local_raw_response:
            data.extend(raw_response.data[0]["formData"])
        return self.process_change_in_water_storage(
            data,
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
            "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas",
            "gri-environment-water-303-4a-third_party",
            "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress",
            "gri-environment-water-303-3b-water_withdrawal_areas_water_stress",
            "gri-environment-water-303-4d-substances_of_concern",
            "gri-environment-water-303-3d-4e-sma",
            "gri-environment-water-303-5c-change_in_water_storage",
            "gri-environment-water-303-5d-sma",
        ]
        # * Total Water Consumption in water stress areas
        self.set_raw_responses(slugs)
        response_data = []
        self.response_data.append({"Total Water Consumption":{
            
        }})
        (
            by_water_consumption,
            by_water_source,
            by_water_type,
            by_water_stress_business_operation,
        ) = self.get_total_water_consumption_in_water_stress_areas()

        (
            by_consumption,
            by_business_operation,
            by_source,
            by_fresh_water,
            by_source_and_water_type,
        ) = self.get_total_water_consumption_in_all_areas()

        response_data.append(
            {
                "water_stress_areas": {
                    "by_water_consumption": by_water_consumption,
                    "by_water_source": by_water_source,
                    "by_water_type": by_water_type,
                    "by_business_operation": by_water_stress_business_operation,
                    "Total Water Discharge by Water type (from water stress area)": by_water_type,
                }
            }
        )
        response_data.append(
            {
                "all_areas": {
                    "by_consumption": by_consumption,
                    "by_business_operation": by_business_operation,
                    "by_source": by_source,
                    "by_fresh_water": by_fresh_water,
                    "by_source_and_watertype": by_source_and_water_type,
                }
            }
        )
        response_data.append(
            self.get_by_location(
                slug="gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas"
            )
        )
        response_data.append(
            self.get_by_location(
                slug="gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress"
            ),
        )

        # Water withdrawal from third-parties
        response_data.append(
            {
                "Water withdrawal from third-parties": self.get_water_withdrawal_from_third_parties()
            }
        )

        # Third-party Water discharge sent to use for other organizations
        response_data.append(
            {
                "Third-party Water discharge sent to use for other organizations": self.get_third_party_discharge_sent_to_use_other_organisations()
            }
        )

        # Change in water storage
        response_data.append(
            {"Change in water storage": self.get_change_in_water_storage()}
        )
        return Response(response_data, status=status.HTTP_200_OK)
