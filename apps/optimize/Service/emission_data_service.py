from datametric.models import EmissionAnalysis
from apps.optimize.models import Scenerio
from sustainapp.models import Location
from decimal import Decimal
from collections import defaultdict
from apps.optimize.filters import EmissionDataFilter
import uuid


class EmissionDataService:
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

        # Area
        self.conversion_factors_area = {
            "si": {
                "base_unit": "km2",
                "m2": Decimal("1.00E-06"),
                "km2": Decimal("1"),
                "ha": Decimal("0.01"),
            },
            "imperial": {"base_unit": "ft2", "ft2": Decimal("1")},
        }

        # Area over Time
        self.conversion_factors_area_over_time = {
            "area_unit": self.conversion_factors_area,
            "time_unit": {
                "si": {
                    "base_unit": "hour",
                    "ms": Decimal("2.78E-07"),
                    "s": Decimal("2.78E-04"),
                    "min": Decimal("1.67E-02"),
                    "hour": Decimal("1"),
                    "day": Decimal("24"),
                    "year": Decimal("8760"),
                }
            },
        }

        # Container over Distance
        self.conversion_factors_container_over_distance = {
            "container_unit": {
                "si": {
                    "base_unit": "containers",
                    "containers": Decimal("1"),
                }
            },
            "distance_unit": {
                "si": {"base_unit": "km", "m": Decimal("0.001"), "km": Decimal("1")},
                "imperial": {
                    "base_unit": "mi",
                    "ft": Decimal("1") / Decimal("5280"),
                    "mi": Decimal("1"),
                    "nmi": Decimal("1.15078"),
                },
            },
        }

        # Data
        self.conversion_factors_data = {
            "si": {
                "base_unit": "MB",
                "MB": Decimal("1"),
                "GB": Decimal("1000"),
                "TB": Decimal("1.00E+06"),
            }
        }

        # Data over Time
        self.conversion_factors_data_over_time = {
            "data_unit": self.conversion_factors_data,
            "time_unit": {
                "si": {
                    "base_unit": "hour",
                    "ms": Decimal("2.78E-07"),
                    "s": Decimal("2.78E-04"),
                    "min": Decimal("1.67E-02"),
                    "hour": Decimal("1"),
                    "day": Decimal("24"),
                    "year": Decimal("8760"),
                }
            },
        }

        # Distance
        self.conversion_factors_distance = {
            "si": {"base_unit": "km", "m": Decimal("0.001"), "km": Decimal("1")},
            "imperial": {
                "base_unit": "mi",
                "ft": Decimal("1") / Decimal("5280"),
                "mi": Decimal("1"),
                "nmi": Decimal("1.15078"),
            },
        }

        # Distance over Time
        self.conversion_factors_distance_over_time = {
            "distance_unit": self.conversion_factors_distance,
            "time_unit": {
                "si": {
                    "base_unit": "hour",
                    "ms": Decimal("2.78E-07"),
                    "s": Decimal("2.78E-04"),
                    "min": Decimal("1.67E-02"),
                    "hour": Decimal("1"),
                    "day": Decimal("24"),
                    "year": Decimal("8760"),
                }
            },
        }

        # Energy
        self.conversion_factors_energy = {
            "si": {
                "base_unit": "kWh",
                "Wh": Decimal("0.001"),
                "kWh": Decimal("1"),
                "MWh": Decimal("1000"),
                "MJ": Decimal("0.2778"),
                "GJ": Decimal("277.8"),
                "TJ": Decimal("277800"),
            },
            "imperial": {
                "base_unit": "BTU",
                "BTU": Decimal("1"),
                "therm": Decimal("100000"),
                "MMBTU": Decimal("1000000"),
            },
        }

        # Number over Time
        self.conversion_factors_number_over_time = {
            "number_unit": {"si": {"base_unit": "numbers", "numbers": Decimal("1")}},
            "time_unit": {
                "si": {
                    "base_unit": "hour",
                    "ms": Decimal("2.78E-07"),
                    "s": Decimal("2.78E-04"),
                    "min": Decimal("1.67E-02"),
                    "hour": Decimal("1"),
                    "day": Decimal("24"),
                    "year": Decimal("8760"),
                }
            },
        }

        # Passenger over Distance
        self.conversion_factors_passenger_over_distance = {
            "passenger_unit": {
                "si": {"base_unit": "passengers", "passengers": Decimal("1")}
            },
            "distance_unit": self.conversion_factors_distance,
        }

        # Number (simple)
        self.conversion_factors_number = {
            "si": {"base_unit": "number of Nights", "number of Nights": Decimal("1")}
        }

        # Time
        self.conversion_factors_time = {
            "si": {
                "base_unit": "hour",
                "ms": Decimal("2.78E-07"),
                "s": Decimal("2.78E-04"),
                "min": Decimal("1.67E-02"),
                "hour": Decimal("1"),
                "day": Decimal("24"),
                "year": Decimal("8760"),
            }
        }

        # Volume
        self.conversion_factors_volume = {
            "si": {
                "base_unit": "l",
                "ml": Decimal("0.001"),
                "l": Decimal("1"),
                "m3": Decimal("1000"),
            },
            "imperial": {
                "base_unit": "gallon_us",
                "gallon_us": Decimal("1"),
                "standard_cubic_foot": Decimal("7.48052"),
                "bbl": Decimal("42"),
            },
        }

        # Weight
        self.conversion_factors_weight = {
            "si": {
                "base_unit": "kg",
                "g": Decimal("0.001"),
                "kg": Decimal("1"),
                "t": Decimal("1000"),
            },
            "imperial": {
                "base_unit": "ton (US short ton)",
                "lb": Decimal("0.0005"),
                "ton (US short ton)": Decimal("1"),
            },
        }

        self.conversion_factors_weight_over_distance = {
            "weight_unit": {
                "si": {
                    "base_unit": "kg",
                    "g": Decimal("0.001"),
                    "kg": Decimal("1"),
                    "t": Decimal("1000"),
                },
                "imperial": {
                    "base_unit": "ton (US short ton)",
                    "lb": Decimal("0.0005"),
                    "ton": Decimal(
                        "1"
                    ),  # Assuming "ton" here means "ton (US short ton)"
                },
            },
            "distance_unit": {
                "si": {
                    "base_unit": "km",
                    "m": Decimal("0.001"),
                    "km": Decimal("1"),
                },
                "imperial": {
                    "base_unit": "mi",
                    "ft": Decimal("1") / Decimal("5280"),
                    "mi": Decimal("1"),
                    "nmi": Decimal("1.15078"),
                },
            },
        }

        self.conversion_factors_weight_over_time = {
            "weight_unit": {
                "si": {
                    "base_unit": "kg",
                    "g": Decimal("0.001"),
                    "kg": Decimal("1"),
                    "t": Decimal("1000"),
                },
                "imperial": {
                    "base_unit": "ton (US short ton)",
                    "lb": Decimal("0.0005"),
                    "ton": Decimal("1"),
                },
            },
            "time_unit": {
                "si": {
                    "base_unit": "hour",
                    "ms": Decimal("2.78E-07"),
                    "s": Decimal("2.78E-04"),
                    "min": Decimal("1.67E-02"),
                    "hour": Decimal("1"),
                    "day": Decimal("24"),
                    "year": Decimal("8760"),
                }
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

    def _convert_single_unit(self, unit, value, conversion_dict):
        for system in ["si", "imperial"]:
            system_dict = conversion_dict.get(system, {})
            if unit in system_dict:
                base_unit = system_dict["base_unit"]
                return value * system_dict[unit], base_unit, None, None
        raise ValueError(f"Unknown unit: {unit}")

    def _convert_dual_units(
        self, unit1, value1, unit2, value2, conversion_dict1, conversion_dict2
    ):
        value1, unit1, _, _ = self._convert_single_unit(unit1, value1, conversion_dict1)
        value2, unit2, _, _ = self._convert_single_unit(unit2, value2, conversion_dict2)
        return value1, unit1, value2, unit2

    def convert_unit(self, unit_type, value1, unit1, value2, unit2):
        # print("Value1:", value1, "Unit1:", unit1, "Value2:", value2, "Unit2:", unit2)
        value1 = Decimal(value1) if value1 is not None else Decimal("0")
        value2 = Decimal(value2) if value2 is not None else Decimal("0")

        # Full pair of values (2D conversions)
        if all([value1, unit1, value2, unit2]):
            if unit_type == "AreaOverTime":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_area_over_time["area_unit"],
                    self.conversion_factors_area_over_time["time_unit"],
                )
            elif unit_type == "ContainerOverDistance":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_container_over_distance["container_unit"],
                    self.conversion_factors_container_over_distance["distance_unit"],
                )
            elif unit_type == "DataOverTime":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_data_over_time["data_unit"],
                    self.conversion_factors_data_over_time["time_unit"],
                )
            elif unit_type == "DistanceOverTime":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_distance_over_time["distance_unit"],
                    self.conversion_factors_distance_over_time["time_unit"],
                )
            elif unit_type == "NumberOverTime":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_number_over_time["number_unit"],
                    self.conversion_factors_number_over_time["time_unit"],
                )
            elif unit_type == "PassengerOverDistance":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_passenger_over_distance["passenger_unit"],
                    self.conversion_factors_passenger_over_distance["distance_unit"],
                )
            elif unit_type == "WeightOverDistance":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_weight_over_distance["weight_unit"],
                    self.conversion_factors_weight_over_distance["distance_unit"],
                )
            elif unit_type == "WeightOverTime":
                return self._convert_dual_units(
                    unit1,
                    value1,
                    unit2,
                    value2,
                    self.conversion_factors_weight_over_time["weight_unit"],
                    self.conversion_factors_weight_over_time["time_unit"],
                )

        # Single value (1D conversions)
        elif (
            value1
            and unit1
            and (not value2 or value2 == "")
            and (not unit2 or unit2 == "")
        ):
            if unit_type == "Area":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_area
                )
                return value1, unit1, None, None
            elif unit_type == "Data":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_data
                )
                return value1, unit1, None, None
            elif unit_type == "Distance":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_distance
                )
                return value1, unit1, None, None
            elif unit_type == "Energy":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_energy
                )
                return value1, unit1, None, None
            elif unit_type == "Number":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_number
                )
                return value1, unit1, None, None
            elif unit_type == "Time":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_time
                )
                return value1, unit1, None, None
            elif unit_type == "Volume":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_volume
                )
                return value1, unit1, None, None
            elif unit_type == "Weight":
                value1, unit1, _, _ = self._convert_single_unit(
                    unit1, value1, self.conversion_factors_weight
                )
                return value1, unit1, None, None

            elif unit_type == "Money":
                # No implementation yet
                return value1, unit1, None, None

        return value1, unit1, value2, unit2

    def get_emission_data(self, request, scenario_id):
        scenario_data = self.get_scenario_data(scenario_id)

        locations = None
        if scenario_data.scenario_by == "organization":
            locations = Location.objects.filter(
                corporateentity__organization=scenario_data.organization
            ).values_list("id", flat=True)
        elif scenario_data.scenario_by == "corporate":
            locations = Location.objects.filter(
                corporateentity=scenario_data.corporate
            ).values_list("id", flat=True)
        else:
            return {"message": "Invalid scenario_by value"}

        queryset = EmissionAnalysis.objects.filter(
            year=scenario_data.base_year, raw_response__locale__in=locations
        ).order_by("activity")

        # Apply filters manually using filterset
        filterset = EmissionDataFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            emission_data = filterset.qs
        else:
            return filterset.errors

        # Apply ordering manually
        ordering = request.GET.getlist(
            "ordering"
        )  # ?ordering=activity&ordering=-region
        if ordering:
            emission_data = emission_data.order_by(*ordering)

        # Initialize the defaultdict to accumulate data
        response = defaultdict(
            lambda: {
                "uuid": "",
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
                "co2e_total": Decimal("0.0"),
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
                data.emission_id,
                converted_unit1,
                converted_unit2,
            )
            key_string = "|".join(str(k) for k in key)

            # Accumulate the quantities for each group
            response[key]["quantity"] += (
                converted_quantity1 if converted_quantity1 else 0
            )
            response[key]["quantity2"] += (
                converted_quantity2 if converted_quantity2 else 0
            )
            response[key]["co2e_total"] += data.co2e_total if data.co2e_total else 0

            # Store the most recent values of other fields (if they are consistent across entries)
            response[key]["uuid"] = uuid.uuid5(uuid.NAMESPACE_DNS, key_string)
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

        response_data = list(response.values())
        return response_data
