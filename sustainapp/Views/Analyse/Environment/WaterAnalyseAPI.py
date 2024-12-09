from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
    get_location_wise_dictionary_data,
)
from decimal import Decimal
from common.utils.value_types import safe_divide, format_decimal_places


class WaterAnalyseByDataPoints(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri-environment-water-303-1b-1c-1d-interaction_with_water",
            1: "gri-environment-water-303-2a-management_water_discharge",
            2: "gri-environment-water-303-2a-profile_receiving_waterbody",
            3: "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas",
            4: "gri-environment-water-303-4a-third_party",
            5: "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress",  # * Water Stress Area
            6: "gri-environment-water-303-3b-water_withdrawal_areas_water_stress",
            7: "gri-environment-water-303-4d-substances_of_concern",
            8: "gri-environment-water-303-3d-4e-sma",
            9: "gri-environment-water-303-5c-change_in_water_storage",
            10: "gri-environment-water-303-5d-sma",
        }
        self.CONVERSION_FACTORS = {
            "litre": "1e-6",
            "cubic meter": "1e-3",
            "million litres per day": "1",
            "megalitre": "1",
            "million litrse per day": "1",
            "kilolitre": "0.001",
        }

        self.water_stress_data = None
        self.fresh_water_data = None
        self.total_water_consumption = 0
        self.total_water_consumption_water_stress = 0

    def calculate_water_consumption(self, withdrawal, discharge, unit):
        return self.convert_to_megalitres(
            value=Decimal(withdrawal), unit=unit
        ) - self.convert_to_megalitres(value=Decimal(discharge), unit=unit)

    def get_consumption_contribution(
        self, withdrawal, discharge, unit, total_water_consumption
    ):
        return (
            safe_divide(
                self.calculate_water_consumption(withdrawal, discharge, unit),
                total_water_consumption,
            )
            * 100
        )

    def get_total_water_consumption_in_water_stress_areas_by_field(
        self, field_name, response_field_name
    ):
        slug = self.slugs[5]
        self.water_stress_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.water_stress_data is None
            else self.water_stress_data
        )

        total_water_consumption = {}
        # * Calculate Total Water Consumption Per Location.
        for location_name in self.water_stress_data:
            consumption_total = 0
            for stress_data in self.water_stress_data[location_name]:
                consumption_total += self.calculate_water_consumption(
                    stress_data["Waterwithdrawal"],
                    stress_data["Waterdischarge"],
                    unit=stress_data["Unit"],
                )
            total_water_consumption[location_name] = consumption_total
        response_list = []
        total_consumption = 0
        for location_name in self.water_stress_data:
            for data in self.water_stress_data[location_name]:
                response_list.append(
                    {
                        "location": location_name,
                        f"{response_field_name}": data[field_name],
                        "contribution": self.get_consumption_contribution(
                            withdrawal=data["Waterwithdrawal"],
                            discharge=data["Waterdischarge"],
                            unit=data["Unit"],
                            total_water_consumption=total_water_consumption[
                                location_name
                            ],
                        ),
                        "consumption": self.calculate_water_consumption(
                            withdrawal=data["Waterwithdrawal"],
                            discharge=data["Waterdischarge"],
                            unit=data["Unit"],
                        ),
                        "water_type": data["Watertype"],
                        "Unit": "Megalitre",
                    }
                )
                total_consumption += self.calculate_water_consumption(
                    withdrawal=data["Waterwithdrawal"],
                    discharge=data["Waterdischarge"],
                    unit=data["Unit"],
                )
        response_list.append(
            {
                "Total": total_consumption,
                "Unit": "Megalitre",
            }
        )
        return response_list

    def get_total_fresh_water_withdrawal_by_field_name(
        self, field_name, response_field_name
    ):
        slug = self.slugs[3]
        self.fresh_water_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.fresh_water_data is None
            else self.fresh_water_data
        )
        total_water_withdrawal = {}
        # * Calculate Total Water Withdrawal Per Location.
        for location_name in self.fresh_water_data:
            consumption_total = 0
            for data in self.fresh_water_data[location_name]:
                consumption_total += self.convert_to_megalitres(
                    data["withdrawal"], data["Unit"]
                )
            total_water_withdrawal[location_name] = consumption_total
        response_list = []
        total_withdrawal = 0
        for location_name in self.fresh_water_data:
            for data in self.fresh_water_data[location_name]:
                response_list.append(
                    {
                        "location": location_name,
                        f"{response_field_name}": data[field_name],
                        "contribution": safe_divide(
                            self.convert_to_megalitres(
                                data["withdrawal"], data["Unit"]
                            ),
                            total_water_withdrawal[location_name],
                        )
                        * 100,
                        "withdrawal": self.convert_to_megalitres(
                            data["withdrawal"], data["Unit"]
                        ),
                        "water_type": data["Watertype"],
                    }
                )
                total_withdrawal += self.convert_to_megalitres(
                    data["withdrawal"], data["Unit"]
                )
        response_list.append(
            {
                "Total": total_withdrawal,
                "Unit": "Megalitre",
            }
        )
        return response_list

    def get_total_water_withdrawal_in_water_stress_areas_by_field_name(
        self, field_name, response_field_name
    ):
        # * This method is not getting used anywhere.
        slug = self.slugs[5]
        self.water_stress_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.water_stress_data is None
            else self.water_stress_data
        )
        total_water_withdrawal = {}
        # * Calculate Total Water Withdrawal Per Location.
        for location_name in self.water_stress_data:
            consumption_total = 0
            for data in self.water_stress_data[location_name]:
                consumption_total += self.convert_to_megalitres(
                    data["Waterwithdrawal"], data["Unit"]
                )
            total_water_withdrawal[location_name] = consumption_total
        response_list = []
        for location_name in self.water_stress_data:
            for data in self.water_stress_data[location_name]:
                response_list.append(
                    {
                        "location": location_name,
                        f"{response_field_name}": data[field_name],
                        "water_stress_area": data["waterstress"],
                        "contribution": safe_divide(
                            self.convert_to_megalitres(
                                data["Waterwithdrawal"], data["Unit"]
                            ),
                            total_water_withdrawal[location_name],
                        )
                        * 100,
                        "withdrawal": self.convert_to_megalitres(
                            data["Waterwithdrawal"], data["Unit"]
                        ),
                        "water_type": data["Watertype"],
                        "source": data["Source"],
                    }
                )
        return response_list

    def get_total_water_consumption_in_water_areas_by_field(
        self, field_name, response_field_name
    ):
        slug = self.slugs[3]
        self.fresh_water_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.fresh_water_data is None
            else self.fresh_water_data
        )

        response_list = []
        total_water_consumption = 0
        for location_name in self.fresh_water_data:
            for data in self.fresh_water_data[location_name]:
                response_list.append(
                    {
                        "location": location_name,
                        f"{response_field_name}": data[field_name],
                        "contribution": self.get_consumption_contribution(
                            withdrawal=data["withdrawal"],
                            discharge=data["discharge"],
                            unit=data["Unit"],
                            total_water_consumption=self.total_water_consumption,
                        ),
                        "consumption": self.calculate_water_consumption(
                            withdrawal=data["withdrawal"],
                            discharge=data["discharge"],
                            unit=data["Unit"],
                        ),
                        "water_type": data["Watertype"],
                        "Unit": "Megalitre",
                    }
                )
                total_water_consumption += self.calculate_water_consumption(
                    withdrawal=data["withdrawal"],
                    discharge=data["discharge"],
                    unit=data["Unit"],
                )
        response_list.append(
            {
                "Unit": "Megalitre",
                "Total": total_water_consumption,
            }
        )
        return response_list

    def convert_to_megalitres(self, value, unit):
        value = Decimal(value)
        unit = unit.lower()
        if unit in self.CONVERSION_FACTORS:
            return format_decimal_places(value * Decimal(self.CONVERSION_FACTORS[unit]))
        else:
            raise ValidationError(f"Unknown unit: {unit}")

    def get_total_water_consumption(self):
        slug = self.slugs[3]
        self.fresh_water_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.fresh_water_data is None
            else self.fresh_water_data
        )
        water_consumption_total_consumption = self.calculate_total_withdrawal_discharge(
            data=self.fresh_water_data,
            withdrawal_key="withdrawal",
            discharge_key="discharge",
            unit="Unit",
        )
        slug = self.slugs[5]
        self.water_stress_data = (
            (
                get_location_wise_dictionary_data(
                    self.data_points.filter(path__slug=slug)
                )
            )
            if self.water_stress_data is None
            else self.water_stress_data
        )
        water_consumption_water_stres_total_consumption = (
            self.calculate_total_withdrawal_discharge(
                data=self.water_stress_data,
                withdrawal_key="Waterwithdrawal",
                discharge_key="Waterdischarge",
                unit="Unit",
            )
        )
        # * Add keys of water_consumption_total_consumption and water_consumption_water_stres_total_consumption in a list
        total_number_of_locations = list(
            set(
                list(water_consumption_total_consumption.keys())
                + list(water_consumption_water_stres_total_consumption.keys())
            )
        )
        # * Create Response List that contains dictionary
        response_list = []
        for location in total_number_of_locations:
            # * Add location, withdrawal and discharge to response_list
            self.total_water_consumption += water_consumption_total_consumption.get(
                location, 0
            )
            self.total_water_consumption_water_stress += (
                water_consumption_water_stres_total_consumption.get(location, 0)
            )
            # * Add water_consumption and water_consumption_water_stress to response_list
            response_list.append(
                {
                    "water_consumption": water_consumption_total_consumption.get(
                        location, 0
                    ),
                    "water_consumption_water_stress": water_consumption_water_stres_total_consumption.get(
                        location, 0
                    ),
                    "Unit": "Megalitre",
                }
            )
        return response_list

    def get_total_water_consumption_by_location(self):
        slug = self.slugs[3]
        self.fresh_water_data = (
            get_location_wise_dictionary_data(self.data_points.filter(path__slug=slug))
            if self.fresh_water_data is None
            else self.fresh_water_data
        )
        water_consumption_total_consumption = self.calculate_total_withdrawal_discharge(
            data=self.fresh_water_data,
            withdrawal_key="withdrawal",
            discharge_key="discharge",
            unit="Unit",
        )
        response_list = []
        total_water_consumption = 0
        for location in water_consumption_total_consumption:
            response_list.append(
                {
                    "location": location,
                    "contribution": safe_divide(
                        water_consumption_total_consumption[location],
                        self.total_water_consumption,
                    )
                    * 100,
                    "total_water_consumption": water_consumption_total_consumption[
                        location
                    ],
                    "Unit": "Megalitre",
                }
            )
            total_water_consumption += water_consumption_total_consumption[location]
        response_list.append(
            {
                "Total": total_water_consumption,
                "Unit": "Megalitre",
            }
        )
        return response_list

    def get_total_water_consumption_by_source(self):
        """
        In this method we have to group by source and if water_type is different for same source, then don't group it.
        """
        slug = self.slugs[3]
        local_fresh_water_data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        grouped_data = {}
        for item in local_fresh_water_data:
            source = item["Source"]
            watertype = item["Watertype"]
            key = (source, watertype)

            withdrawal_ml = self.convert_to_megalitres(item["withdrawal"], item["Unit"])
            discharge_ml = self.convert_to_megalitres(item["discharge"], item["Unit"])

            if key not in grouped_data:
                grouped_data[key] = {
                    "Source": source,
                    "Watertype": watertype,
                    "consumption": self.calculate_water_consumption(
                        withdrawal_ml, discharge_ml, unit="megalitre"
                    ),
                    "Unit": "Megalitre",
                }
            else:
                grouped_data[key]["consumption"] += self.calculate_water_consumption(
                    withdrawal_ml, discharge_ml, "megalitre"
                )
        response_list = []
        total_water_consumption = 0
        for key, value in grouped_data.items():
            response_list.append(
                {
                    "source": key[0],
                    "watertype": key[1],
                    "consumption": value["consumption"],
                    "Unit": value["Unit"],
                    "contribution": safe_divide(
                        value["consumption"], self.total_water_consumption
                    )
                    * 100,
                }
            )
            total_water_consumption += value["consumption"]
        response_list.append(
            {
                "Total": total_water_consumption,
                "Unit": "Megalitre",
            }
        )
        return response_list

    def get_total_fresh_water_calculated_field_by_business_operation(
        self, field_to_be_calculated: str
    ):
        slug = self.slugs[3]
        local_fresh_water_data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        grouped_data = {}
        total_calculated_ml = 0
        for item in local_fresh_water_data:
            business_op = item["Businessoperations"]
            calculated_field_ml = self.convert_to_megalitres(
                item[field_to_be_calculated], item["Unit"]
            )
            if business_op not in grouped_data:
                grouped_data[business_op] = {
                    "Businessoperations": business_op,
                    field_to_be_calculated: calculated_field_ml,
                    "Unit": "Megalitre",
                }
            else:
                grouped_data[business_op][field_to_be_calculated] += calculated_field_ml
            total_calculated_ml += calculated_field_ml

        response_list = []
        total_field_calculated = 0
        for key, value in grouped_data.items():
            response_list.append(
                {
                    "business_operation": key,
                    field_to_be_calculated: value[field_to_be_calculated],
                    "Unit": value["Unit"],
                    "contribution": safe_divide(
                        value[field_to_be_calculated], total_calculated_ml
                    )
                    * 100,
                }
            )
            total_field_calculated += value[field_to_be_calculated]
        response_list.append(
            {
                "Total": total_field_calculated,
                "Unit": "Megalitre",
            }
        )
        return response_list

    def get_total_fresh_water_withdrawal_by_source_water_stress_area(self):
        slug = self.slugs[5]
        local_water_stress_area_data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        groups = {}
        total_withdrawal = 0

        for entry in local_water_stress_area_data:
            key = (entry["Source"], entry["waterstress"], entry["Watertype"])
            withdrawal = entry["Waterwithdrawal"]

            # Convert to megalitres for consistency
            withdrawal_ml = self.convert_to_megalitres(withdrawal, entry["Unit"])

            if key in groups:
                groups[key] += withdrawal_ml
            else:
                groups[key] = withdrawal_ml

            total_withdrawal += withdrawal_ml

        result = []
        total_withdrawal_ml = 0
        for (source, waterstress, watertype), withdrawal in groups.items():
            contribution = safe_divide(withdrawal, total_withdrawal) * 100

            result.append(
                {
                    "source": source,
                    "water_stress": waterstress,
                    "water_type": watertype,
                    "total_withdrawal": withdrawal,
                    "contribution": format_decimal_places(contribution),
                    "Unit": "Megalitre",
                }
            )
            total_withdrawal_ml += withdrawal
        result.append(
            {
                "Total": total_withdrawal_ml,
                "Unit": "Megalitre",
            }
        )
        return result

    def get_total_water_discharge_by_water_type_from_water_stress_area(self):
        slug = self.slugs[5]
        local_water_stress_area_data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        groups = {}
        total_discharge = 0

        for entry in local_water_stress_area_data:
            key = (entry["waterstress"], entry["Watertype"])
            discharge = entry["Waterdischarge"]

            # Convert to megalitres for consistency
            discharge_ml = self.convert_to_megalitres(discharge, entry["Unit"])

            if key in groups:
                groups[key] += discharge_ml
            else:
                groups[key] = discharge_ml

            total_discharge += discharge_ml

        result = []
        total_discharge_ml = 0
        for (waterstress, watertype), discharge in groups.items():
            contribution = safe_divide(discharge, total_discharge) * 100

            result.append(
                {
                    "water_stress": waterstress,
                    "water_type": watertype,
                    "total_discharge": discharge,
                    "contribution": format_decimal_places(contribution),
                    "Unit": "Megalitre",
                }
            )
            total_discharge_ml += discharge
        result.append(
            {
                "Total": total_discharge_ml,
                "Unit": "Megalitre",
            }
        )
        return result

    def get_total_fresh_water_discharge_by_source_water_stress_area(self):
        slug = self.slugs[5]
        local_water_stress_area_data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        groups = {}
        total_discharge = 0

        for entry in local_water_stress_area_data:
            key = (
                entry["Businessoperations"],
                entry["waterstress"],
            )
            discharge = entry["Waterdischarge"]

            # Convert to megalitres for consistency
            discharge_ml = self.convert_to_megalitres(discharge, entry["Unit"])

            if key in groups:
                groups[key] += discharge_ml
            else:
                groups[key] = discharge_ml

            total_discharge += discharge_ml

        result = []
        total_discharge_ml = 0
        for (business_operation, waterstress), discharge in groups.items():
            contribution = safe_divide(discharge, total_discharge) * 100

            result.append(
                {
                    "water_stress": waterstress,
                    "business_operation": business_operation,
                    "total_discharge": discharge,
                    "contribution": format_decimal_places(contribution),
                    "Unit": "Megalitre",
                }
            )
            total_discharge_ml += discharge
        result.append(
            {
                "Total": total_discharge_ml,
                "Unit": "Megalitre",
            }
        )
        return result

    def get_total_fresh_water_calculate_field_by_location_country(
        self, field_to_be_calculated
    ):
        slug = self.slugs[3]
        self.fresh_water_data = (
            self.fresh_water_data
            if self.fresh_water_data
            else get_location_wise_dictionary_data(
                self.data_points.filter(path__slug=slug)
            )
        )
        location_totals = {}
        total_calculation = 0

        # Calculate total withdrawal for each location
        for location, entries in self.fresh_water_data.items():
            location_total = sum(
                self.convert_to_megalitres(entry[field_to_be_calculated], entry["Unit"])
                for entry in entries
            )
            location_totals[location] = location_total
            total_calculation += location_total

        results = []
        total_field_calculation = 0
        for location, calculated_field in location_totals.items():
            contribution = safe_divide(calculated_field, total_calculation) * 100
            results.append(
                {
                    "location": location,
                    "contribution": contribution,
                    f"total_water_{field_to_be_calculated}": calculated_field,
                    "Unit": "Megalitre",
                }
            )
            total_field_calculation += calculated_field
        results.append(
            {
                "Total": total_field_calculation,
                "Unit": "Megalitre",
            }
        )

        return results

    def get_third_party_water_discharge_sent_to_use_for_other_organizations(self):
        slug = self.slugs[4]
        data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        total_volume = sum(
            self.convert_to_megalitres(entry["Volume"], entry["Unit"]) for entry in data
        )
        result = []
        for entry in data:
            result.append(
                {
                    "volume": self.convert_to_megalitres(
                        entry["Volume"], entry["Unit"]
                    ),
                    "contribution": safe_divide(
                        self.convert_to_megalitres(entry["Volume"], entry["Unit"]),
                        total_volume,
                    )
                    * 100,
                    "Unit": "Megalitre",
                }
            )
        return result

    def get_total_water_calculated_field_by_water_type(
        self, field_to_be_calculated: str
    ):
        slug = self.slugs[3]
        self.fresh_water_data = (
            self.fresh_water_data
            if self.fresh_water_data
            else get_location_wise_dictionary_data(
                self.data_points.filter(path__slug=slug)
            )
        )
        data = []
        for _ in self.fresh_water_data:
            data.extend(self.fresh_water_data[_])

        grouped_data = {}
        total_calculated_field = 0

        # First pass - group and sum withdrawals
        for entry in data:
            key = (entry["Watertype"], entry["Source"])
            calculated_field = self.convert_to_megalitres(
                entry[field_to_be_calculated], entry["Unit"]
            )

            if key in grouped_data:
                grouped_data[key] += calculated_field
            else:
                grouped_data[key] = calculated_field

            total_calculated_field += calculated_field

        response = []
        total_calculated_field_ml = 0
        for (water_type, source), calculated_field in grouped_data.items():
            contribution = safe_divide(calculated_field, total_calculated_field) * 100
            response.append(
                {
                    "water_type": water_type,
                    "source": source,
                    "contribution": contribution,
                    f"total_water_{field_to_be_calculated}": calculated_field,
                    "Unit": "Megalitre",
                }
            )
            total_calculated_field_ml += calculated_field
        response.append(
            {
                "Total": total_calculated_field_ml,
                "Unit": "Megalitre",
            }
        )
        return response

    def get_water_withdrawal_from_third_parties(self):
        slug = self.slugs[6]
        data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        grouped_data = {}
        total_quantity = Decimal("0")
        # First pass - convert and sum quantities
        for entry in data:
            source = entry["Source"]
            quantity = Decimal(entry["Quantity"])
            unit = entry["Unit"].lower()

            converted_quantity = self.convert_to_megalitres(quantity, unit)

            if source not in grouped_data:
                grouped_data[source] = Decimal("0")

            grouped_data[source] += converted_quantity
            total_quantity += converted_quantity

        # Second pass - format results with percentages
        result = []
        total_quantity_ml = 0
        for source, quantity in grouped_data.items():
            contribution = safe_divide(quantity, total_quantity) * 100

            result.append(
                {
                    "source": source,
                    "quantity": format_decimal_places(quantity),
                    "Unit": "Megalitre",
                    "contribution": f"{format_decimal_places(contribution)}%",
                }
            )
            total_quantity_ml += quantity
        result.append(
            {
                "Total": total_quantity_ml,
                "Unit": "Megalitre",
            }
        )
        return result

    def get_change_in_water_storage(self):
        slug = self.slugs[9]
        data = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=slug)
        )
        result = []
        for entry in data:
            result.append(
                {
                    "Unit": "Megalitre",
                    "change_in_water_storage": self.convert_to_megalitres(
                        entry["Reporting1"], entry["Unit"]
                    )
                    - self.convert_to_megalitres(entry["Reporting2"], entry["Unit"]),
                }
            )
        return result

    def calculate_total_withdrawal_discharge(
        self, data, withdrawal_key, discharge_key, unit
    ):
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
                withdrawal = record[withdrawal_key]
                discharge = record[discharge_key]
                withdrawal = self.convert_to_megalitres(withdrawal, record[unit])
                discharge = self.convert_to_megalitres(discharge, record[unit])
                total_withdrawal += withdrawal
                total_discharge += discharge

            # Store the results in the summary dictionary
            summary[location] = format_decimal_places(
                self.calculate_water_consumption(
                    total_withdrawal, total_discharge, unit="Megalitre"
                )
            )

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
        # * Table Name: Total Water Consumption
        response_data["total_water_consumption"] = self.get_total_water_consumption()
        # * Table Name: Total Water Consumption in water stress areas
        response_data["total_water_consumption_in_water_stress_areas_by_area"] = (
            self.get_total_water_consumption_in_water_stress_areas_by_field(
                field_name="waterstress", response_field_name="water_stress_area"
            )
        )
        # * Table Name: Total Water Consumption by business operation
        response_data["total_water_consumption_by_business_operation"] = (
            self.get_total_water_consumption_in_water_areas_by_field(
                field_name="Businessoperations",
                response_field_name="business_operation",
            )
        )
        # * Table Name: Total Water Consumption by Location
        response_data["total_water_consumption_by_location"] = (
            self.get_total_water_consumption_by_location()
        )

        # * Table Name: Total Water Consumption by source
        response_data["total_water_consumption_by_source"] = (
            self.get_total_water_consumption_by_source()
        )
        # * Table Name: Total Fresh Water withdrawal by business operation
        response_data["total_fresh_water_withdrawal_by_business_operation"] = (
            self.get_total_fresh_water_calculated_field_by_business_operation(
                "withdrawal"
            )
        )

        # * Table Name: Total Fresh Water withdrawal by source (from water stress area)
        response_data["total_fresh_water_withdrawal_by_source"] = (
            self.get_total_fresh_water_withdrawal_by_source_water_stress_area()
        )
        # * Table Name: Total Fresh Water withdrawal by Location/Country
        response_data["get_total_fresh_water_withdrawal_by_location_country"] = (
            self.get_total_fresh_water_calculate_field_by_location_country(
                field_to_be_calculated="withdrawal"
            )
        )
        # * Table Name: Total Water withdrawal by Water type
        response_data["total_water_withdrawal_by_water_type"] = (
            self.get_total_water_calculated_field_by_water_type("withdrawal")
        )
        # * Table Name: Water withdrawal from third-parties
        response_data["water_withdrawal_from_third_parties"] = (
            self.get_water_withdrawal_from_third_parties()
        )
        # * Table Name: Total Water Discharge by Location
        response_data["get_total_fresh_water_discharge_by_location_country"] = (
            self.get_total_fresh_water_calculate_field_by_location_country(
                field_to_be_calculated="discharge"
            )
        )
        # * Total Water Discharge by source and type of water
        response_data["total_water_discharge_by_water_type"] = (
            self.get_total_water_calculated_field_by_water_type("discharge")
        )
        # * Table Name: Total Water Discharge (from water stress area) by Business Operation
        response_data[
            "total_water_discharge_from_water_stress_area_by_business_operation"
        ] = self.get_total_fresh_water_discharge_by_source_water_stress_area()

        # * Table Name: Total Water Discharge by Business Operation
        response_data["total_fresh_water_discharge_by_business_operation"] = (
            self.get_total_fresh_water_calculated_field_by_business_operation(
                "discharge"
            )
        )
        # * Table Name: Total Water Discharge by Water type (from water stress area)
        response_data["total_water_discharge_by_water_type_from_water_stress_area"] = (
            self.get_total_water_discharge_by_water_type_from_water_stress_area()
        )

        # * Table Name: Third-party Water discharge sent to use for other organizations
        response_data[
            "third_party_water_discharge_sent_to_use_for_other_organizations"
        ] = self.get_third_party_water_discharge_sent_to_use_for_other_organizations()

        # * Table Name:  Change in water storage
        response_data["change_in_water_storage"] = self.get_change_in_water_storage()
        response_data["total_water_area_consumption"] = self.total_water_consumption
        response_data["total_water_area_consumption_water_stress_areas"] = (
            self.total_water_consumption_water_stress
        )

        return Response(response_data, status=status.HTTP_200_OK)
