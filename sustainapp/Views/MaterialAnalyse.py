from datametric.models import RawResponse
from sustainapp.models import Location, Corporateentity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from common.utils.value_types import format_decimal_places, safe_divide
from decimal import Decimal
import logging

logger = logging.getLogger("django.log")


class GetMaterialAnalysis(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define conversion factors and unit hierarchy
        self.conversion_factors = {
            "Milligram": 1e-3,  # to grams (g)
            "Gram": 1,  # grams is the base unit for weight
            "Kilogram Kg": 1e3,  # to grams (g)
            "Metric ton": 1e6,  # to grams (g)
            "Pound Lb": 453.592,  # to grams (g)
            "US short ton (tn)": 907184.74,  # to grams (g)
            "Milliliter": 1,  # milliliter is the base unit for liquid volume
            "Liter": 1e3,  # to milliliters (ml)
            "Fluid Ounce fl Oz": 29.5735,  # to milliliters (ml)
            "Quart Qt": 946.353,  # to milliliters (ml)
            "Gallon Gal": 3785.41,  # to milliliters (ml)
            "Pint Pt": 473.176,  # to milliliters (ml)
            "Cubic centimeter cm3": 1,  # cubic centimeter is the base unit for cubic volume
            "Cubic decimeter dm3": 1e3,  # to cubic centimeters (cm³)
            "Cubic meter m3": 1e6,  # to cubic centimeters (cm³)
            "Cubic foot ft3": 28316.8,  # to cubic centimeters (cm³)
        }

        self.unit_hierarchy = {
            "weight": [
                "Milligram",
                "Gram",
                "Kilogram Kg",
                "Metric ton",
                "Pound Lb",
                "US short ton (tn)",
            ],
            "volume": [
                "Milliliter",
                "Liter",
                "Fluid Ounce fl Oz",
                "Quart Qt",
                "Gallon Gal",
                "Pint Pt",
            ],
            "cubic_volume": [
                "Cubic centimeter cm3",
                "Cubic decimeter dm3",
                "Cubic meter m3",
                "Cubic foot ft3",
            ],
        }

        # To identify unit categories

        self.unit_categories = {
            "Milligram": "weight",
            "Gram": "weight",
            "Kilogram Kg": "weight",
            "Metric ton": "weight",
            "Pound Lb": "weight",
            "US short ton (tn)": "weight",
            "Milliliter": "volume",
            "Liter": "volume",
            "Fluid Ounce fl Oz": "volume",
            "Quart Qt": "volume",
            "Gallon Gal": "volume",
            "Pint Pt": "volume",
            "Cubic centimeter cm3": "cubic_volume",
            "Cubic decimeter dm3": "cubic_volume",
            "Cubic meter m3": "cubic_volume",
            "Cubic foot ft3": "cubic_volume",
        }

    def convert_to_cubic_cm(self, value, from_unit):
        """
        Convert any volume unit to cubic centimeters (cm³)

        Args:
            value (float): The value to convert
            from_unit (str): The source unit

        Returns:
            float: Value in cubic centimeters
            None: If conversion not possible
        """
        try:
            if from_unit not in self.conversion_factors:
                raise ValueError(f"Invalid unit: {from_unit}")

            # Convert directly to cubic centimeters using conversion factor
            return format_decimal_places(
                value * Decimal(self.conversion_factors[from_unit])
            )

        except TypeError as e:
            logger.error(f"Conversion error: {str(e)}")
            return 0

    def get_material_data(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Function to gather data from table renewable and non-renewable materials,
        and convert them to the highest unit within their respective categories."""

        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            locale__in=location,
            # location__in=location,
        )

        renewable_materials_dict = defaultdict(
            lambda: {
                "material_type": "",
                "material_category": "",
                "source": "",
                "total_quantity": Decimal(0.0),
                "units": "",
                "data_source": "",
            }
        )

        all_units = {"weight": set(), "volume": set(), "cubic_volume": set()}

        # Aggregate quantities for initial grouping
        for rw in raw_responses:
            for data in rw.data:
                material_type = data.get("Typeofmaterial", "")
                material_category = data.get("Materialsused", "")
                source = data.get("Source", "")
                units = data.get("Unit", "")
                data_source = data.get("Datasource", "")
                total_quantity = data.get("Totalweight", 0)
                try:
                    total_quantity = Decimal(total_quantity)
                except ValueError:
                    # If total_waste cannot be converted to float, skip this data entry
                    continue

                key = (material_type, material_category, source, units, data_source)

                renewable_materials_dict[key]["material_type"] = material_type
                renewable_materials_dict[key]["material_category"] = material_category
                renewable_materials_dict[key]["source"] = source
                renewable_materials_dict[key]["units"] = units
                renewable_materials_dict[key]["data_source"] = data_source
                renewable_materials_dict[key]["total_quantity"] += total_quantity

                # Identify unit category
                category = self.unit_categories.get(units)
                if category:
                    all_units[category].add(units)
                else:
                    print(f"Warning: Unit '{units}' not categorized.")

        # Determine the highest unit for each group
        grouped_materials = []
        processed_keys = set()  # Set to track processed group keys

        for (
            material_type,
            material_category,
            source,
            _,
            data_source,
        ), value in renewable_materials_dict.items():
            # Identify all units used for this group
            relevant_units = [
                units
                for (_, cat, src, units, ds) in renewable_materials_dict
                if cat == material_category and src == source and ds == data_source
            ]

            if not relevant_units:
                continue

            # Determine categories for all units in this group
            categories = set(self.unit_categories.get(un) for un in relevant_units)

            # Initialize a list to store results for each category
            grouped_results = []

            for category in categories:
                if not category:
                    logger.warning(
                        f"Warning: No category found for units {relevant_units}"
                    )
                    continue

                # Filter units by category
                category_units = [
                    units
                    for units in relevant_units
                    if self.unit_categories.get(units) == category
                ]

                # Ensure there's at least one unit for this category
                if not category_units:
                    print(
                        f"Warning: No units found for category {category} in {relevant_units}"
                    )
                    continue

                # Determine the highest unit for this category
                try:
                    highest_unit = max(
                        category_units,
                        key=lambda u: self.unit_hierarchy[category].index(u),
                    )
                except ValueError as ve:
                    logger.error(f"Error: {ve}")
                    logger.error(f"Relevant units: {category_units}")
                    logger.error(f"Unit hierarchy: {self.unit_hierarchy[category]}")
                    continue

                # Initialize group key with highest unit
                group_key = (
                    material_type,
                    material_category,
                    source,
                    highest_unit,
                    data_source,
                )

                # Check if group_key has already been processed
                if group_key in processed_keys:
                    continue

                # Mark group_key as processed
                processed_keys.add(group_key)

                total_quantity_converted = Decimal(0.0)

                # Sum up quantities for all relevant units converted to highest unit
                for key, sub_value in renewable_materials_dict.items():
                    if (
                        key[1] == material_category
                        and key[2] == source
                        and key[4] == data_source
                        and key[3]
                        in category_units  # Only consider units in this category
                    ):
                        units = key[3]
                        total_quantity = sub_value["total_quantity"]

                        # Convert to the highest unit
                        if (
                            units in self.conversion_factors
                            and highest_unit in self.conversion_factors
                        ):
                            total_quantity_converted += format_decimal_places(
                                (
                                    Decimal(total_quantity)
                                    * Decimal(self.conversion_factors[units])
                                    / Decimal(self.conversion_factors[highest_unit])
                                )
                            )
                        else:
                            total_quantity_converted += format_decimal_places(
                                total_quantity
                            )

                # Store the grouped material information for this category
                grouped_results.append(
                    {
                        "material_type": material_type,
                        "material_category": material_category,
                        "source": source,
                        "units": highest_unit,
                        "data_source": data_source,
                        "total_quantity": format_decimal_places(
                            total_quantity_converted
                        ),
                    }
                )

            # Extend grouped_materials with results for all categories
            grouped_materials.extend(grouped_results)

        return grouped_materials

    def get_reclaimed_materials(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Funtion which will gather and structure data from table reclaimed materials,
        it distinguish data by path slug send on function arguments,
        it calcualte percentage of reclaimed products
        Field used to calculate:
        Total Amounts of product and packaging materials recycled(material_type) / Total Amount of products sold * 100
        """
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            locale__in=location,
            # location__in=location,
        )
        reclaimed_materials_dict = defaultdict(
            lambda: {
                "type_of_product": "",
                "product_code": "",
                "product_name": "",
                "total_quantity": Decimal(0.0),
                "percentage_of_reclaimed_products": "",
            }
        )
        total_product_packaging = Decimal(0.0)
        for rw in raw_responses:
            for data in rw.data:
                type_of_product = data["Typesofproducts"]
                product_code = data["Productcode"]
                product_name = data["Productname"]
                total_quantity = data["Amountofproducts"]
                total_quantity_unit = data["Unit"]
                total_amount_of_product_packaging = data["Amountsproduct"]
                total_amount_of_product_packaging_unit = data["Unit2"]
                try:
                    total_quantity = self.convert_to_cubic_cm(
                        Decimal(total_quantity), from_unit=total_quantity_unit
                    )
                    total_amount_of_product_packaging = self.convert_to_cubic_cm(
                        Decimal(total_amount_of_product_packaging),
                        from_unit=total_amount_of_product_packaging_unit,
                    )
                except ValueError:
                    # If total_waste cannot be converted to float, skip this data entry
                    continue

                key = (type_of_product, product_code, product_name)

                reclaimed_materials_dict[key]["type_of_product"] = type_of_product

                reclaimed_materials_dict[key]["product_code"] = product_code
                reclaimed_materials_dict[key]["product_name"] = product_name
                reclaimed_materials_dict[key]["total_quantity"] += Decimal(
                    total_quantity
                )
                total_product_packaging += total_amount_of_product_packaging

        for key, value in reclaimed_materials_dict.items():
            value["percentage_of_reclaimed_products"] = format_decimal_places(
                safe_divide(value["total_quantity"], total_product_packaging) * 100
            )
        reclaimed_materials = list(reclaimed_materials_dict.values())
        return reclaimed_materials

    def get_recycled_materials(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Gathers and structure data for table recycled materials.
        Calculates percentage in the selected reporting period time
        Fields used to calculate percentage:
        Total Amount of recycled input material used / Total Amount of material recycled * 100
        """
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            locale__in=location,
            # location__in=location,
        )
        recycled_materials_dict = defaultdict(
            lambda: {
                "type_of_recycled_material_used": "",
                "total_recycled_input_materials_used": Decimal(0.0),
                "percentage_of_recycled_input_materials_used": Decimal(0.0),
            }
        )
        total_material_recycled = Decimal(0.0)
        for rw in raw_responses:
            for data in rw.data:
                type_of_recycled_material = data["Typeofrecycledmaterialused"]
                recycled_input_material_used = data["Amountofrecycledinputmaterialused"]
                recycled_input_material_used_unit = data["Unit"]
                material_recycled = data["Amountofmaterialrecycled"]
                material_recycled_unit = data["Unit2"]
                try:
                    recycled_input_material_used = self.convert_to_cubic_cm(
                        Decimal(recycled_input_material_used),
                        from_unit=recycled_input_material_used_unit,
                    )
                    material_recycled = self.convert_to_cubic_cm(
                        Decimal(material_recycled), from_unit=material_recycled_unit
                    )
                except ValueError:
                    # If total_waste cannot be converted to float, skip this data entry
                    continue
                total_material_recycled += material_recycled

                key = type_of_recycled_material
                recycled_materials_dict[key]["type_of_recycled_material_used"] = (
                    type_of_recycled_material
                )
                recycled_materials_dict[key]["total_recycled_input_materials_used"] += (
                    recycled_input_material_used
                )

        for key, values in recycled_materials_dict.items():
            values["percentage_of_recycled_input_materials_used"] = (
                format_decimal_places(
                    safe_divide(
                        values["total_recycled_input_materials_used"],
                        Decimal(total_material_recycled),
                    )
                )
                * 100
            )

        recycled_materials = list(recycled_materials_dict.values())
        return recycled_materials

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        organisation = serializer.validated_data.get("organisation", None)
        corporate = serializer.validated_data.get("corporate", None)
        location = serializer.validated_data.get("location", None)
        start = serializer.validated_data.get("start", None)
        end = serializer.validated_data.get("end", None)
        if location:
            locations = Location.objects.filter(pk=location.id)
        elif corporate:
            locations = Location.objects.filter(corporateentity=corporate)
        elif organisation:
            corporate_entity = Corporateentity.objects.filter(
                organization_id=organisation.id
            ).values_list("id", flat=True)
            locations = Location.objects.filter(corporateentity__in=corporate_entity)
        else:
            return Response(
                {"error": "Please provide either organisation, corporate or location"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        location_names = locations  # .values_list("name", flat=True)

        renewable_materials = self.get_material_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-1a-renewable_materials",
        )

        non_renewable_materials = self.get_material_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-1a-non_renewable_materials",
        )

        recycled_materials = self.get_recycled_materials(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-2a-recycled_input_materials",
        )

        reclaimed_materials = self.get_reclaimed_materials(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-materials-301-3a-3b-reclaimed_products",
        )

        return Response(
            {
                "renewable_materials": renewable_materials,
                "non_renewable_materials": non_renewable_materials,
                "recycled_materials": recycled_materials,
                "reclaimed_materials": reclaimed_materials,
            },
            status=status.HTTP_200_OK,
        )
