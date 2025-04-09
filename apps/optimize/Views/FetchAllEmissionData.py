from rest_framework.views import APIView
from rest_framework.response import Response
from datametric.models import EmissionAnalysis
from ..models import Scenerio
from sustainapp.models import Location
from decimal import Decimal
from collections import defaultdict


class FetchEmissionData(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit_types = [
            "Area",
            "AreaOverTime",
            "ContainerOverDistance",
            "Data",
            "DataOverTime",
            "Distance",
            "DistanceOverTime",
            "Energy",
            "Money",
            "Number",
            "NumberOverTime",
            "PassengerOverDistance",
            "Time",
            "Volume",
            "Weight",
            "WeightOverDistance",
            "WeightOverTime",
        ]

        self.conversion_factors_area = {
            "m2": Decimal("1.00E-06"),
            "km2": Decimal("1"),
            "ft2": Decimal("9.29E-08"),
            "ha": Decimal("0.01"),
        }

        self.conversion_factors_area_over_time = {
            "area_unit": {
                "m2": Decimal("1.00E-06"),
                "km2": Decimal("1"),
                "ft2": Decimal("9.29E-08"),
                "ha": Decimal("0.01"),
            },
            "time_unit": {
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),  # Default time unit is "hour"
                "day": Decimal("2.40E+01"),
                "year": Decimal("8.76E+03"),
            },
        }

        self.conversion_factors_container_over_distance = {
            "container_unit": {
                "containers": Decimal(
                    "1"
                ),  # Default unit for containers is "containers"
            },
            "distance_unit": {
                "m": Decimal("0.001"),
                "km": Decimal("1"),
                "ft": Decimal("3.05E-04"),
                "mi": Decimal("1.60934"),
                "nmi": Decimal("1.852"),
            },
        }

        self.conversion_factors_data = {
            "MB": Decimal("1"),
            "GB": Decimal("1000"),
            "TB": Decimal("1.00E+06"),
        }

        self.conversion_factors_data_over_time = {
            "data_unit": {
                "MB": Decimal("1"),
                "GB": Decimal("1000"),
                "TB": Decimal("1.00E+06"),
            },
            "time_unit": {
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),  # Default time unit is "hour"
                "day": Decimal("2.40E+01"),
                "year": Decimal("8.76E+03"),
            },
        }

        self.conversion_factors_distance = {
            "m": Decimal("0.001"),
            "km": Decimal("1"),
            "ft": Decimal("3.05E-04"),
            "mi": Decimal("1.60934"),
            "nmi": Decimal("1.852"),
        }

        self.conversion_factors_distance_over_time = {
            "distance_unit": {
                "m": Decimal("0.001"),
                "km": Decimal("1"),
                "ft": Decimal("3.05E-04"),
                "mi": Decimal("1.60934"),
                "nmi": Decimal("1.852"),
            },
            "time_unit": {
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),  # Default time unit is "hour"
                "day": Decimal("2.40E+01"),
                "year": Decimal("8.76E+03"),
            },
        }

        self.conversion_factors_energy = {
            "Wh": Decimal("0.001"),
            "kWh": Decimal("1"),
            "MWh": Decimal("1000"),
            "MJ": Decimal("2.78E-01"),
            "GJ": Decimal("2.78E+02"),
            "TJ": Decimal("2.78E+05"),
            "BTU": Decimal("2.93E-04"),
            "therm": Decimal("2.93E+01"),
            "MMBTU": Decimal("2.93E+02"),
        }

        self.conversion_factors_number_over_time = {
            "number_unit": {
                "numbers": Decimal("1"),  # Default unit for number is "numbers"
            },
            "time_unit": {
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),  # Default time unit is "hour"
                "day": Decimal("2.40E+01"),
                "year": Decimal("8.76E+03"),
            },
        }

        self.conversion_factors_passenger_over_distance = {
            "passenger_unit": {
                "passengers": Decimal("1"),  # Default unit for passenger is "passenger"
            },
            "distance_unit": {
                "m": Decimal("0.001"),
                "km": Decimal("1"),
                "ft": Decimal("3.05E-04"),
                "mi": Decimal("1.60934"),
                "nmi": Decimal("1.852"),
            },
        }

        self.conversion_factors_number = {
            "number_units": {
                "number of Nights": Decimal("1"),  # Default unit for "number of Nights"
            }
        }
        self.conversion_factors_time = {
            "ms": Decimal("2.78E-07"),
            "s": Decimal("2.78E-04"),
            "min": Decimal("1.67E-02"),
            "hour": Decimal("1"),  # Default time unit is "hour"
            "day": Decimal("2.40E+01"),
            "year": Decimal("8.76E+03"),
        }

        self.conversion_factors_volume = {
            "ml": Decimal("0.001"),
            "l": Decimal("1"),  # Default volume unit is "l"
            "m3": Decimal("1000"),
            "standard_cubic_foot": Decimal("28.3168"),
            "gallon_us": Decimal("3.79E+00"),
            "bbl": Decimal("158.987"),
        }

        self.conversion_factors_weight = {
            "kg": Decimal(0.001),
            "lb": Decimal(0.00045359237),
            "ton (US short ton)": Decimal(0.90718474),
            "g": Decimal(0.000001),
            "t": Decimal(1),
        }

        self.conversion_factors_weight_over_distance = {
            "weight_unit": {
                "g": Decimal("0.001"),
                "kg": Decimal("1"),  # Default unit for weight is "kg"
                "t": Decimal("1000"),
                "ton": Decimal("907.185"),
                "lb": Decimal("0.453592"),
            },
            "distance_unit": {
                "m": Decimal("0.001"),
                "km": Decimal("1"),
                "ft": Decimal("3.05E-04"),
                "mi": Decimal("1.60934"),
                "nmi": Decimal("1.852"),
            },
        }

        self.conversion_factors_weight_over_time = {
            "weight_unit": {
                "g": Decimal("0.001"),
                "kg": Decimal("1"),  # Default weight unit is "kg"
                "t": Decimal("1000"),
                "ton": Decimal("907.185"),
                "lb": Decimal("0.453592"),
            },
            "time_unit": {
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),  # Default time unit is "hour"
                "day": Decimal("2.40E+01"),
                "year": Decimal("8.76E+03"),
            },
        }

    def get_scenario_data(self, scenario_id):
        scenario_data = Scenerio.objects.get(id=scenario_id)
        return scenario_data

    def extract_unit_type(self, activity_string, unit_types):
        # Split the string by " - "
        split_string = activity_string.split(" - ")

        for i in range(
            2, len(split_string)
        ):  # Is it okay to always start from index 2? Ask this with team later
            unit_type_candidate = split_string[i].strip()
            if unit_type_candidate in unit_types:
                return unit_type_candidate

        return None

    def convert_unit(self, unit_type, value1, unit1, value2, unit2):
        # Convert input value to Decimal if necessary
        print("Value1:", value1, "Unit1:", unit1, "Value2:", value2, "Unit2:", unit2)
        value1 = Decimal(value1) if value1 is not None else 0
        value2 = Decimal(value2) if value2 is not None else 0
        result_unit1 = None
        result_unit2 = None

        if all([value1, unit1, value2, unit2]):
            if unit_type == "AreaOverTime":
                conversion_factor = self.conversion_factors_area_over_time
                value1 = value1 * conversion_factor["area_unit"][unit1]
                unit1 = "km2"
                value2 = value2 * conversion_factor["time_unit"][unit2]
                unit2 = "hour"
                return value1, unit1, value2, unit2

            elif unit_type == "ContainerOverDistance":
                conversion_factor = self.conversion_factors_container_over_distance
                value1 = value1 * conversion_factor["container_unit"][unit1]
                unit1 = "containers"
                value2 = value2 * conversion_factor["distance_unit"][unit2]
                unit2 = "km"
                return value1, unit1, value2, unit2

            elif unit_type == "DataOverTime":
                conversion_factor = self.conversion_factors_data_over_time
                value1 = value1 * conversion_factor["data_unit"][unit1]
                unit1 = "MB"
                value2 = value2 * conversion_factor["time_unit"][unit2]
                unit2 = "hour"
                return value1, unit1, value2, unit2

            elif unit_type == "DistanceOverTime":
                conversion_factor = self.conversion_factors_distance_over_time
                value1 = value1 * conversion_factor["distance_unit"][unit1]
                unit1 = "km"
                value2 = value2 * conversion_factor["time_unit"][unit2]
                unit2 = "hour"
                return value1, unit1, value2, unit2

            elif unit_type == "NumberOverTime":
                conversion_factor = self.conversion_factors_number_over_time
                value1 = value1 * conversion_factor["number_unit"][unit1]
                unit1 = "numbers"
                value2 = value2 * conversion_factor["time_unit"][unit2]
                unit2 = "hour"
                return value1, unit1, value2, unit2

            elif unit_type == "PassengerOverDistance":
                conversion_factor = self.conversion_factors_passenger_over_distance
                value1 = value1 * conversion_factor["passenger_unit"][unit1]
                unit1 = "passengers"
                value2 = value2 * conversion_factor["distance_unit"][unit2]
                unit2 = "km"
                return value1, unit1, value2, unit2

            elif unit_type == "WeightOverDistance":
                conversion_factor = self.conversion_factors_weight_over_distance
                value1 = value1 * conversion_factor["weight_unit"][unit1]
                unit1 = "kg"
                value2 = value2 * conversion_factor["distance_unit"][unit2]
                unit2 = "km"
                return value1, unit1, value2, unit2

            elif unit_type == "WeightOverTime":
                conversion_factor = self.conversion_factors_weight_over_time
                value1 = value1 * conversion_factor["weight_unit"][unit1]
                unit1 = "kg"
                value2 = value2 * conversion_factor["time_unit"][unit2]
                unit2 = "hour"
                return value1, unit1, value2, unit2
        elif (
            value1
            and unit1
            and (not value2 or value2 == "" and not unit2 or unit2 == "")
        ):
            if unit_type == "Area":
                conversion_factor = self.conversion_factors_area
                value1 = value1 * conversion_factor[unit1]
                unit1 = "km2"
                return value1, unit1, None, None

            elif unit_type == "Data":
                conversion_factor = self.conversion_factors_data
                value1 = value1 * conversion_factor[unit1]
                unit1 = "MB"
                return value1, unit1, None, None

            elif unit_type == "Distance":
                conversion_factor = self.conversion_factors_distance
                value1 = value1 * conversion_factor[unit1]
                unit1 = "km"
                return value1, unit1, None, None

            elif unit_type == "Energy":
                conversion_factor = self.conversion_factors_energy
                value1 = value1 * conversion_factor[unit1]
                unit1 = "kWh"
                return value1, unit1, None, None

            elif unit_type == "Money":
                # Need to implement this
                return value1, unit1, None, None

            elif unit_type == "Number":
                conversion_factor = self.conversion_factors_number
                value1 = value1 * conversion_factor[unit1]
                unit1 = "number of Nights"
                return value1, unit1, None, None

            elif unit_type == "Time":
                conversion_factor = self.conversion_factors_time
                value1 = value1 * conversion_factor[unit1]
                unit1 = "hour"
                return value1, unit1, None, None

            elif unit_type == "Volume":
                conversion_factor = self.conversion_factors_volume
                value1 = value1 * conversion_factor[unit1]
                unit1 = "l"
                return value1, unit1, None, None

            elif unit_type == "Weight":
                conversion_factor = self.conversion_factors_weight
                value1 = value1 * conversion_factor[unit1]
                unit1 = "t"
                return value1, unit1, None, None

        return value1, result_unit1, value2, result_unit2

    def get(self, request, scenario_id):
        scenario_data = self.get_scenario_data(scenario_id)

        locations = None
        if scenario_data.scenario_by == "organization":
            locations = Location.objects.filter(
                corporateentity__organization=scenario_data.organization
            ).values_list("id", flat=True)
        elif scenario_data.scenario_by == "corporate":
            locations = Location.objects.filter(corporateentity=scenario_data.corporate)
        else:
            return Response({"message": "Invalid scenario_by value"}, status=400)

        emission_data = EmissionAnalysis.objects.filter(
            year=scenario_data.base_year, raw_response__locale__in=locations
        )

        # Initialize the defaultdict to accumulate data
        response = defaultdict(
            lambda: {
                "scope": "",
                "category": "",
                "sub_category": "",
                "quantity": Decimal("0.0"),
                "unit": "",
                "quantity2": Decimal("0.0"),
                "unit2": "",
                "unit_type": "",
                "factor_id": "",
                "activity_name": "",
                "activity_id": "",
                "region": "",
            }
        )

        # Loop through emission data and accumulate values
        for data in emission_data:
            unit_type = self.extract_unit_type(data.activity, self.unit_types)
            (
                converted_quantity1,
                converted_unit1,
                converted_quantity2,
                converted_unit2,
            ) = self.convert_unit(
                unit_type, data.quantity, data.unit1, data.quantity2, data.unit2
            )

            # Create the key based on the group by fields
            key = (
                data.scope,
                data.category,
                data.subcategory,
                data.activity,
                data.region,
                unit_type,
            )

            # Accumulate the quantities for each group
            response[key]["quantity"] += (
                converted_quantity1 if converted_quantity1 else 0
            )
            response[key]["quantity2"] += (
                converted_quantity2 if converted_quantity2 else 0
            )

            # Store the most recent values of other fields (if they are consistent across entries)
            response[key]["scope"] = data.scope
            response[key]["category"] = data.category
            response[key]["sub_category"] = data.subcategory
            response[key]["unit"] = converted_unit1
            response[key]["unit2"] = converted_unit2
            response[key]["unit_type"] = unit_type
            response[key]["factor_id"] = data.emission_id
            response[key]["activity_name"] = data.activity
            response[key]["activity_id"] = data.activity_id
            response[key]["region"] = data.region

        # Convert the defaultdict to a list of dictionaries to return as response
        return Response(list(response.values()), status=200)
