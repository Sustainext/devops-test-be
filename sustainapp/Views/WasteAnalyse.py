from datametric.models import RawResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from django.db.models import Prefetch
from rest_framework import serializers
from sustainapp.models import Location


class GetWasteAnalysis(APIView):

    def get_waste_data(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        self.conversion_factors = {
            "Kgs": 0.001,
            "lbs": 0.00045359237,
            "ton (US short ton)": 0.90718474,
            "g": 0.000001,
            "t (metric tons)": 1,
        }
        """Function to gather data from table waste, it distinguish data by path slug send on function arguments"""
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            location__in=location,
        )

        waste_generated_dict = defaultdict(
            lambda: {
                "material_type": "",
                "contribution": 0.0,
                "total_waste": 0.0,
                "units": "t (metric tons)",
            }
        )
        waste_generated_location = defaultdict(
            lambda: {
                "location": "",
                "material_type": "",
                "contribution": 0.0,
                "total_waste": 0.0,
                "units": "t (metric tons)",
            }
        )
        waste_generated_by_category = defaultdict(
            lambda: {
                "material_type": "",
                "contribution": 0.0,
                "total_waste": 0.0,
                "units": "t (metric tons)",
            }
        )

        total_waste_generated = 0.0

        for rw in raw_responses:
            location = rw.location
            for data in rw.data:
                material_type = data["WasteType"]
                total_waste = float(data["Wastegenerated"])
                units = data["Unit"]
                if units in self.conversion_factors:
                    total_waste *= self.conversion_factors[units]
                else:
                    raise ValueError(f"Unsupported unit: {units}")

                # Update total waste generated
                total_waste_generated += total_waste

                # Update waste by material type (table 1)
                waste_generated_dict[material_type]["material_type"] = material_type
                waste_generated_dict[material_type]["total_waste"] += total_waste

                # Update waste by location and material type (table 2)
                location_key = f"{location}-{material_type}"
                waste_generated_location[location_key]["location"] = location
                waste_generated_location[location_key]["material_type"] = material_type
                waste_generated_location[location_key]["total_waste"] += total_waste

                # Update waste by category (table 3)
                waste_category = data["Wastecategory"]
                waste_generated_by_category[waste_category][
                    "material_type"
                ] = waste_category
                waste_generated_by_category[waste_category][
                    "total_waste"
                ] += total_waste

        # Calculate contributions
        for key, value in waste_generated_dict.items():
            waste_generated_dict[key]["contribution"] = round(
                ((value["total_waste"] / total_waste_generated) * 100), 2
            )

        for key, value in waste_generated_location.items():
            waste_generated_location[key]["contribution"] = round(
                ((value["total_waste"] / total_waste_generated) * 100), 2
            )

        for key, value in waste_generated_by_category.items():
            waste_generated_by_category[key]["contribution"] = round(
                ((value["total_waste"] / total_waste_generated) * 100), 2
            )

        waste_generated = list(waste_generated_dict.values())
        waste_generated_location_list = list(waste_generated_location.values())
        waste_generated_by_category_list = list(waste_generated_by_category.values())

        # Add total waste generated to the end of the list
        total_waste = {"total_waste_generated": total_waste_generated}
        waste_generated.append(total_waste)
        waste_generated_location_list.append(total_waste)
        waste_generated_by_category_list.append(total_waste)

        return (
            waste_generated,
            waste_generated_location_list,
            waste_generated_by_category_list,
        )

    def get_waste_diverted_from_data(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Function to gather data from table waste_diverted_from_disposal, it distinguishes data by path slug sent on function arguments"""
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            location__in=location,
        )
        waste_diverted_from_data = defaultdict(
            lambda: {
                "recovery_operation": "",
                "material_type": "",
                "total_waste": 0.0,
                "contribution": 0.0,
                "units": "t (metric tons)",
            }
        )
        hazardous_waste_diverted_from_data = defaultdict(
            lambda: {
                "material_type": "",
                "total_waste": 0.0,
                "units": "t (metric tons)",
                "recycled_quantity": 0.0,
                "preparation_of_reuse_quantity": 0.0,
                "other_quantity": 0.0,
                "recycled_percentage": 0.0,
                "preparation_of_reuse_percentage": 0.0,
                "other_percentage": 0.0,
                "site": "",
            }
        )
        non_hazardous_waste_diverted_from_data = defaultdict(
            lambda: {
                "material_type": "",
                "total_waste": 0.0,
                "units": "t (metric tons)",
                "recycled_quantity": 0.0,
                "preparation_of_reuse_quantity": 0.0,
                "other_quantity": 0.0,
                "recycled_percentage": 0.0,
                "preparation_of_reuse_percentage": 0.0,
                "other_percentage": 0.0,
                "site": "",
            }
        )

        total_waste_diverted = 0.0

        for rw in raw_responses:
            for data in rw.data:
                recovery_operation = data["RecoveryOperations"]
                material_type = data["WasteType"]
                total_waste = float(data["Wastediverted"])
                units = data["Unit"]
                if units in self.conversion_factors:
                    total_waste *= self.conversion_factors[units]
                else:
                    raise ValueError(f"Unsupported unit: {units}")

                key = f"{recovery_operation}-{material_type}"

                # Update total waste diverted (table 5)
                total_waste_diverted += total_waste
                waste_diverted_from_data[key]["recovery_operation"] = recovery_operation
                waste_diverted_from_data[key]["material_type"] = material_type
                waste_diverted_from_data[key]["total_waste"] += total_waste

                # Get data for hazardous and non-hazardous waste diverted from disposal (table 6 and 7)
                waste_type = data["WasteType"]
                site = data["Site"]
                waste_category = data["Wastecategory"]
                waste_key = f"{waste_type}-{site}"

                if waste_category == "Hazardous":
                    if recovery_operation == "Preparation for reuse":
                        hazardous_waste_diverted_from_data[waste_key][
                            "preparation_of_reuse_quantity"
                        ] += total_waste
                    elif recovery_operation == "Recycling":
                        hazardous_waste_diverted_from_data[waste_key][
                            "recycled_quantity"
                        ] += total_waste
                    else:
                        hazardous_waste_diverted_from_data[waste_key][
                            "other_quantity"
                        ] += total_waste

                    # Update hazardous waste diverted (table 6)
                    hazardous_waste_diverted_from_data[waste_key][
                        "material_type"
                    ] = waste_type
                    hazardous_waste_diverted_from_data[waste_key][
                        "total_waste"
                    ] += total_waste
                    hazardous_waste_diverted_from_data[waste_key]["site"] = site
                else:
                    if recovery_operation == "Preparation for reuse":
                        non_hazardous_waste_diverted_from_data[waste_key][
                            "preparation_of_reuse_quantity"
                        ] += total_waste
                    elif recovery_operation == "Recycling":
                        non_hazardous_waste_diverted_from_data[waste_key][
                            "recycled_quantity"
                        ] += total_waste
                    else:
                        non_hazardous_waste_diverted_from_data[waste_key][
                            "other_quantity"
                        ] += total_waste

                    # Update non-hazardous waste diverted (table 7)
                    non_hazardous_waste_diverted_from_data[waste_key][
                        "material_type"
                    ] = waste_type
                    non_hazardous_waste_diverted_from_data[waste_key][
                        "total_waste"
                    ] += total_waste
                    non_hazardous_waste_diverted_from_data[waste_key]["site"] = site

        for key, value in waste_diverted_from_data.items():
            waste_diverted_from_data[key]["contribution"] = round(
                ((value["total_waste"] / total_waste_diverted) * 100), 2
            )

        for key, value in hazardous_waste_diverted_from_data.items():
            quantity = value["total_waste"]
            if quantity > 0:
                hazardous_waste_diverted_from_data[key]["recycled_percentage"] = round(
                    (value["recycled_quantity"] / quantity) * 100, 2
                )
                hazardous_waste_diverted_from_data[key][
                    "preparation_of_reuse_percentage"
                ] = round((value["preparation_of_reuse_quantity"] / quantity) * 100, 2)
                hazardous_waste_diverted_from_data[key]["other_percentage"] = round(
                    (value["other_quantity"] / quantity) * 100, 2
                )
            # Deleting those values which were used for calculation, as we dont want to show this on API
            del hazardous_waste_diverted_from_data[key]["recycled_quantity"]
            del hazardous_waste_diverted_from_data[key]["preparation_of_reuse_quantity"]
            del hazardous_waste_diverted_from_data[key]["other_quantity"]

        for key, value in non_hazardous_waste_diverted_from_data.items():
            quantity = value["total_waste"]
            if quantity > 0:
                non_hazardous_waste_diverted_from_data[key]["recycled_percentage"] = (
                    round((value["recycled_quantity"] / quantity) * 100, 2)
                )
                non_hazardous_waste_diverted_from_data[key][
                    "preparation_of_reuse_percentage"
                ] = round((value["preparation_of_reuse_quantity"] / quantity) * 100, 2)
                non_hazardous_waste_diverted_from_data[key]["other_percentage"] = round(
                    (value["other_quantity"] / quantity) * 100, 2
                )
            # Deleting those values which were used for calculation, as we dont want to show this on API
            del non_hazardous_waste_diverted_from_data[key]["recycled_quantity"]
            del non_hazardous_waste_diverted_from_data[key][
                "preparation_of_reuse_quantity"
            ]
            del non_hazardous_waste_diverted_from_data[key]["other_quantity"]

        waste_diverted_from_data_list = list(waste_diverted_from_data.values())
        hazardous_waste_diverted_from_data_list = list(
            hazardous_waste_diverted_from_data.values()
        )
        non_hazardous_waste_diverted_from_data_list = list(
            non_hazardous_waste_diverted_from_data.values()
        )

        # Adding Total Waste Generated at the end
        total_waste = {"total_waste_generated": total_waste_diverted}
        waste_diverted_from_data_list.append(total_waste)

        total_hazardeous_waste_generated = 0.0
        for waste in hazardous_waste_diverted_from_data_list:
            total_hazardeous_waste_generated += float(waste["total_waste"])

        total_hazardeous_waste = {
            "total_waste_generated": total_hazardeous_waste_generated
        }
        hazardous_waste_diverted_from_data_list.append(total_hazardeous_waste)

        total_non_hazardeous_waste_generated = 0.0
        for waste in non_hazardous_waste_diverted_from_data_list:
            total_non_hazardeous_waste_generated += float(waste["total_waste"])

        total_non_hazardeous_waste = {
            "total_waste_generated": total_non_hazardeous_waste_generated
        }
        non_hazardous_waste_diverted_from_data_list.append(total_non_hazardeous_waste)

        return (
            waste_diverted_from_data_list,
            hazardous_waste_diverted_from_data_list,
            non_hazardous_waste_diverted_from_data_list,
        )

    def get_waste_directed_to_data(
        self, location, start_year, end_year, start_month, end_month, path_slug
    ):
        """Function to gather data from table waste_diverted_from_disposal, it distinguishes data by path slug sent on function arguments"""
        raw_responses = RawResponse.objects.filter(
            path__slug=path_slug,
            year__range=(start_year, end_year),
            month__range=(start_month, end_month),
            location__in=location,
        )
        waste_diverted_from_data = defaultdict(
            lambda: {
                "disposal_method": "",
                "material_type": "",
                "total_waste": 0.0,
                "contribution": 0.0,
                "units": "t (metric tons)",
            }
        )
        hazardous_waste_directed_to_data = defaultdict(
            lambda: {
                "material_type": "",
                "total_waste": 0.0,
                "units": "t (metric tons)",
                "inceneration_with_energy_quantity": 0.0,
                "inceneration_without_energy_quantity": 0.0,
                "landfill_quantity": 0.0,
                "other_disposal_quantity": 0.0,
                "external_quantity": 0.0,
                "inceneration_with_energy_percentage": 0.0,
                "inceneration_without_energy_percentage": 0.0,
                "landfill_percentage": 0.0,
                "other_disposal_percentage": 0.0,
                "external_percentage": 0.0,
                "site": "",
            }
        )
        non_hazardous_waste_directed_to_data = defaultdict(
            lambda: {
                "material_type": "",
                "total_waste": 0.0,
                "units": "t (metric tons)",
                "inceneration_with_energy_quantity": 0.0,
                "inceneration_without_energy_quantity": 0.0,
                "landfill_quantity": 0.0,
                "other_disposal_quantity": 0.0,
                "external_quantity": 0.0,
                "inceneration_with_energy_percentage": 0.0,
                "inceneration_without_energy_percentage": 0.0,
                "landfill_percentage": 0.0,
                "other_disposal_percentage": 0.0,
                "external_percentage": 0.0,
                "site": "",
            }
        )

        total_waste_diverted = 0.0

        for rw in raw_responses:
            for data in rw.data:
                disposal_method = data["Methodofdisposal"]
                material_type = data["WasteType"]
                total_waste = float(data["Wastedisposed"])
                units = data["Unit"]
                if units in self.conversion_factors:
                    total_waste *= self.conversion_factors[units]
                else:
                    raise ValueError(f"Unsupported unit: {units}")

                key = f"{disposal_method}-{material_type}"

                # Update total waste diverted (table 4)
                total_waste_diverted += total_waste
                waste_diverted_from_data[key]["disposal_method"] = disposal_method
                waste_diverted_from_data[key]["material_type"] = material_type
                waste_diverted_from_data[key]["total_waste"] += total_waste

                # Get data for hazardous and non-hazardous waste diverted from disposal (table 8 and 9)
                waste_type = data["WasteType"]
                site = data["Site"]
                waste_category = data["Wastecategory"]
                waste_key = f"{waste_type}-{site}"

                if waste_category == "Hazardous":
                    if (
                        disposal_method
                        == "Inceneration (with energy recovery) for reuse"
                    ):
                        hazardous_waste_directed_to_data[waste_key][
                            "inceneration_with_energy_quantity"
                        ] += total_waste
                    elif disposal_method == "Inceneration (without energy recovery)":
                        hazardous_waste_directed_to_data[waste_key][
                            "inceneration_without_energy_quantity"
                        ] += total_waste
                    elif disposal_method == "Landfilling":
                        hazardous_waste_directed_to_data[waste_key][
                            "landfill_quantity"
                        ] += total_waste
                    elif disposal_method == "External Vendor":
                        hazardous_waste_directed_to_data[waste_key][
                            "external_quantity"
                        ] += total_waste
                    else:
                        hazardous_waste_directed_to_data[waste_key][
                            "other_disposal_quantity"
                        ] += total_waste

                    # Update hazardous waste diverted (table 6)
                    hazardous_waste_directed_to_data[waste_key][
                        "material_type"
                    ] = waste_type
                    hazardous_waste_directed_to_data[waste_key][
                        "total_waste"
                    ] += total_waste
                    hazardous_waste_directed_to_data[waste_key]["site"] = site
                else:
                    if (
                        disposal_method
                        == "Inceneration (with energy recovery) for reuse"
                    ):
                        non_hazardous_waste_directed_to_data[waste_key][
                            "inceneration_with_energy_quantity"
                        ] += total_waste
                    elif disposal_method == "Inceneration (without energy recovery)":
                        non_hazardous_waste_directed_to_data[waste_key][
                            "inceneration_without_energy_quantity"
                        ] += total_waste
                    elif disposal_method == "Landfilling":
                        non_hazardous_waste_directed_to_data[waste_key][
                            "landfill_quantity"
                        ] += total_waste
                    elif disposal_method == "External Vendor":
                        non_hazardous_waste_directed_to_data[waste_key][
                            "external_quantity"
                        ] += total_waste
                    else:
                        non_hazardous_waste_directed_to_data[waste_key][
                            "other_disposal_quantity"
                        ] += total_waste

                    # Update hazardous waste diverted (table 6)
                    non_hazardous_waste_directed_to_data[waste_key][
                        "material_type"
                    ] = waste_type
                    non_hazardous_waste_directed_to_data[waste_key][
                        "total_waste"
                    ] += total_waste
                    non_hazardous_waste_directed_to_data[waste_key]["site"] = site

        for key, value in waste_diverted_from_data.items():
            waste_diverted_from_data[key]["contribution"] = round(
                ((value["total_waste"] / total_waste_diverted) * 100), 2
            )

        for key, value in hazardous_waste_directed_to_data.items():
            quantity = value["total_waste"]
            if quantity > 0:
                hazardous_waste_directed_to_data[key][
                    "inceneration_with_energy_percentage"
                ] = round(
                    (value["inceneration_with_energy_quantity"] / quantity) * 100, 2
                )
                hazardous_waste_directed_to_data[key][
                    "inceneration_without_energy_percentage"
                ] = round(
                    (value["inceneration_without_energy_quantity"] / quantity) * 100, 2
                )

                hazardous_waste_directed_to_data[key]["landfill_percentage"] = round(
                    (value["landfill_quantity"] / quantity) * 100, 2
                )

                hazardous_waste_directed_to_data[key]["external_percentage"] = round(
                    (value["external_quantity"] / quantity) * 100, 2
                )

                hazardous_waste_directed_to_data[key]["other_disposal_percentage"] = (
                    round((value["other_disposal_quantity"] / quantity) * 100, 2)
                )
            del hazardous_waste_directed_to_data[key][
                "inceneration_with_energy_quantity"
            ]
            del hazardous_waste_directed_to_data[key][
                "inceneration_without_energy_quantity"
            ]

            # Deleting those values which were used for calculation, as we dont want to show this on API
            del hazardous_waste_directed_to_data[key]["landfill_quantity"]
            del hazardous_waste_directed_to_data[key]["other_disposal_quantity"]
            del hazardous_waste_directed_to_data[key]["external_quantity"]

        for key, value in non_hazardous_waste_directed_to_data.items():
            quantity = value["total_waste"]
            if quantity > 0:
                non_hazardous_waste_directed_to_data[key][
                    "inceneration_with_energy_percentage"
                ] = round(
                    (value["inceneration_with_energy_quantity"] / quantity) * 100, 2
                )
                non_hazardous_waste_directed_to_data[key][
                    "inceneration_without_energy_percentage"
                ] = round(
                    (value["inceneration_without_energy_quantity"] / quantity) * 100, 2
                )

                non_hazardous_waste_directed_to_data[key]["landfill_percentage"] = (
                    round((value["landfill_quantity"] / quantity) * 100, 2)
                )

                non_hazardous_waste_directed_to_data[key]["external_percentage"] = (
                    round((value["external_quantity"] / quantity) * 100, 2)
                )

                non_hazardous_waste_directed_to_data[key][
                    "other_disposal_percentage"
                ] = round((value["other_disposal_quantity"] / quantity) * 100, 2)
            del non_hazardous_waste_directed_to_data[key][
                "inceneration_with_energy_quantity"
            ]
            del non_hazardous_waste_directed_to_data[key][
                "inceneration_without_energy_quantity"
            ]

            # Deleting those values which were used for calculation, as we dont want to show this on API
            del non_hazardous_waste_directed_to_data[key]["landfill_quantity"]
            del non_hazardous_waste_directed_to_data[key]["other_disposal_quantity"]
            del non_hazardous_waste_directed_to_data[key]["external_quantity"]

        waste_diverted_from_data_list = list(waste_diverted_from_data.values())
        hazardous_waste_diverted_from_data_list = list(
            hazardous_waste_directed_to_data.values()
        )
        non_hazardous_waste_diverted_from_data_list = list(
            non_hazardous_waste_directed_to_data.values()
        )

        # Adding Total Waste Generated at the end
        total_waste = {"total_waste_generated": total_waste_diverted}
        waste_diverted_from_data_list.append(total_waste)

        total_hazardeous_waste_generated = 0.0
        for waste in hazardous_waste_diverted_from_data_list:
            total_hazardeous_waste_generated += float(waste["total_waste"])

        total_hazardeous_waste = {
            "total_waste_generated": total_hazardeous_waste_generated
        }
        hazardous_waste_diverted_from_data_list.append(total_hazardeous_waste)

        total_non_hazardeous_waste_generated = 0.0
        for waste in non_hazardous_waste_diverted_from_data_list:
            total_non_hazardeous_waste_generated += float(waste["total_waste"])

        total_non_hazardeous_waste = {
            "total_waste_generated": total_non_hazardeous_waste_generated
        }
        non_hazardous_waste_diverted_from_data_list.append(total_non_hazardeous_waste)

        return (
            waste_diverted_from_data_list,
            hazardous_waste_diverted_from_data_list,
            non_hazardous_waste_diverted_from_data_list,
        )

    def get(self, request):
        """
        Get Waste Analysis API
        """
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        self.organisation = serializer.validated_data.get("organisation", None)
        self.corporate = serializer.validated_data.get("corporate", None)
        self.location = serializer.validated_data.get("location", None)
        start = serializer.validated_data.get("start", None)
        end = serializer.validated_data.get("end", None)

        if self.organisation and self.corporate and self.location:
            self.locations = Location.objects.filter(id=self.location.id)
        elif (
            self.organisation is None and self.corporate and self.location is None
        ) or (self.organisation and self.corporate and self.location is None):
            self.locations = self.corporate.location.all()
        elif (
            self.organisation and self.corporate is None and self.location is None
        ) or (self.organisation is None and self.corporate and self.location):
            self.locations = Location.objects.prefetch_related(
                Prefetch(
                    "corporateentity",
                    queryset=self.organisation.corporatenetityorg.all(),
                )
            )
        else:
            raise serializers.ValidationError(
                "Not send any of the following fields: organisation, corporate, location"
            )

        location_names = self.locations.values_list("name", flat=True)
        (
            waste_generated_by_material,
            waste_generated_by_location,
            waste_generated_by_category,
        ) = self.get_waste_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-waste-306-3a-3b-waste_generated",
        )
        (
            waste_diverted_from_data,
            hazardeous_waste_diverted_from,
            non_hazardeous_waste_diverted_from,
        ) = self.get_waste_diverted_from_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-waste-306-4b-4c-4d-waste_diverted_from_disposal",
        )
        (
            waste_directed_to_data,
            hazardeous_waste_directed_to_data,
            non_hazardeous_waste_directed_to_data,
        ) = self.get_waste_directed_to_data(
            location_names,
            start.year,
            end.year,
            start.month,
            end.month,
            "gri-environment-waste-306-5a-5b-5c-5d-5e-waste_diverted_to_disposal",
        )
        final_response = {
            "waste_generated_by_material": waste_generated_by_material,
            "waste_generated_by_location": waste_generated_by_location,
            "hazardous_and_non_hazardous_waste_composition": waste_generated_by_category,
            "waste_directed_to_disposal_by_material_type": waste_directed_to_data,
            "waste_diverted_from_disposal_by_material_type": waste_diverted_from_data,
            "hazardous_waste_diverted_form_disposal": hazardeous_waste_diverted_from,
            "non_hazardeous_waste_diverted_from_disposal": non_hazardeous_waste_diverted_from,
            "hazardeous_waste_directed_to_disposal": hazardeous_waste_directed_to_data,
            "non_hazardeous_waste_directed_to_disposal": non_hazardeous_waste_directed_to_data,
        }
        return Response(final_response, status=status.HTTP_200_OK)
