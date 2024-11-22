from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)

from django.db.models import Prefetch
from rest_framework import serializers
from datametric.utils.analyse import filter_by_start_end_dates
from common.utils.value_types import safe_divide


class EnergyAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def process_energy_data(self, path, sno, total_energy_consumption_within_org=None):
        conversions = {
            "Joules": {"GJ": 1e-9, "KWh": 0.00000027778},
            "KJ": {"GJ": 1e-6, "KWh": 0.00027778},
            "Wh": {"GJ": 0.0000036, "KWh": 0.001},
            "KWh": {"GJ": 0.0036, "KWh": 1},
            "GJ": {"GJ": 1, "KWh": 277.778},
            "MMBtu": {"GJ": 1.055056, "KWh": 293.071},
        }

        consumed_ene_query = RawResponse.objects.filter(
            # location__in=self.locations.values_list("name", flat=True),
            locale__in=self.locations,
            path__slug=path,
            client__id=self.clients_id,
        ).filter(filter_by_start_end_dates(self.from_date, self.to_date))

        if not consumed_ene_query:
            if sno in [3, 4, 5, 6]:
                return [], 0, 0
            else:
                return [], [], 0, 0

        data = []
        for obj in consumed_ene_query:
            data.extend(obj.data)

        grouped_data = {}
        grand_total_renewable_gj = 0
        grand_total_non_renewable_gj = 0
        grand_total_gj = 0
        grand_total_kwh = 0

        def get_quantity_in_units(item, unit_key, quantity_key="Quantity"):
            try:
                quantity = float(item[quantity_key])
            except ValueError:
                print(f"Error: Quantity '{item[quantity_key]}' is not a valid number.")
                return 0, 0
            unit = item[unit_key]
            return (
                conversions[unit]["GJ"] * quantity,
                conversions[unit]["KWh"] * quantity,
            )

        key_generators = {
            1: lambda item: (item["EnergyType"], item["Source"], item["Renewable"]),
            2: lambda item: (
                item["EnergyType"],
                item["Source"],
                item["Typeofentity"],
                item["Nameofentity"].capitalize(),
                item["Renewable"],
            ),
            3: lambda item: (item["EnergyType"], item["Purpose"].capitalize()),
            4: lambda item: (
                item["Typeofintervention"],
                item["Energytypereduced"],
                item["Energyreductionis"],
                item["Baseyear"],
                item["Methodologyused"],
            ),
            5: lambda item: item["ProductServices"].capitalize(),
            6: lambda item: (item["Organizationmetric"], item["Metricunit"]),
            7: lambda item: (
                item["EnergyType"],
                item["Source"],
                item["Purpose"].capitalize(),
                item["Renewable"],
            ),
        }

        for item in data:

            if "Purpose" in item:
                item["Purpose"] = item["Purpose"].capitalize()
            elif "Nameofentity" in item:
                item["Nameofentity"] = item["Nameofentity"].capitalize()
            elif "ProductServices" in item:
                item["ProductServices"] = item["ProductServices"].capitalize()

            try:
                if sno < 4 or sno == 7:
                    quantity_in_gj, _ = get_quantity_in_units(item, "Unit")
                elif sno == 4:
                    quantity_in_gj, quantity_in_kwh = get_quantity_in_units(
                        item, "Unit", "Quantitysavedduetointervention"
                    )
                elif sno == 5:
                    quantity_in_gj, quantity_in_kwh = get_quantity_in_units(
                        item, "Unit"
                    )
                elif sno == 6:
                    organization_metric = item["Organizationmetric"]
                    metric_quantity = float(item["Metricquantity"])
                    metric_unit = item["Metricunit"]
                    key = (organization_metric, metric_unit)
                    if key not in grouped_data:
                        grouped_data[key] = {"Metricquantity": 0}
                    grouped_data[key]["Metricquantity"] += metric_quantity
                    continue

                key = key_generators[sno](item)
                if key not in grouped_data:
                    grouped_data[key] = 0
                grouped_data[key] += quantity_in_gj

                if sno in [4, 5]:
                    grand_total_gj += quantity_in_gj
                    grand_total_kwh += quantity_in_kwh
                else:
                    if sno in [1, 2, 7]:
                        if item["Renewable"] == "Renewable":
                            grand_total_renewable_gj += quantity_in_gj
                        else:
                            grand_total_non_renewable_gj += quantity_in_gj
                    else:
                        grand_total_gj += quantity_in_gj
            except KeyError as e:
                print(f"Missing field {e} in data item, skipping this item.")
                continue

        renewable_data = []
        non_renewable_data = []
        other_data = []

        record_creators = {
            1: lambda key, total: {
                "Energy_type": key[0],
                "Source": key[1],
                "Quantity": round(total, 3),
                "Unit": "GJ",
            },
            2: lambda key, total: {
                "Energy_type": key[0],
                "Source": key[1],
                "Entity_type": key[2],
                "Entity_name": key[3],
                "Quantity": round(total, 3),
                "Unit": "GJ",
            },
            3: lambda key, total: {
                "Energy_type": key[0],
                "Purpose": key[1],
                "Quantity": round(total, 3),
                "Unit": "GJ",
            },
            4: lambda key, total: {
                "Type_of_intervention": key[0],
                "Energy_type": key[1],
                "Energy_reduction": key[2],
                "Base_year": key[3],
                "Methodology": key[4],
                "Quantity1": round(total, 3),
                "Unit1": "GJ",
                "Quantity2": round(total * 277.778, 3),
                "Unit2": "KWh",
            },
            5: lambda key, total: {
                "Product": key,
                "Quantity1": round(total, 3),
                "Unit1": "GJ",
                "Quantity2": round(total * 277.778, 3),
                "Unit2": "KWh",
            },
            6: lambda key, total: {
                "Energy_quantity": total_energy_consumption_within_org,
                "Organization_metric": key[0],
                "Energy_intensity1": safe_divide(
                    total_energy_consumption_within_org, total["Metricquantity"]
                ),
                "Unit1": f"GJ/{key[1]}",
                "Energy_intensity2": safe_divide(
                    total_energy_consumption_within_org,
                    total["Metricquantity"] * 277.778,
                ),
                "Unit2": f"KWh/{key[1]}",
            },
            7: lambda key, total: {
                "Energy_type": key[0],
                "Source": key[1],
                "Purpose": key[2],
                "Quantity": round(total, 3),
                "Unit": "GJ",
            },
        }

        for key, total_quantity in grouped_data.items():
            energy_record = record_creators[sno](key, total_quantity)

            if sno in [1, 2, 7]:
                if key[-1] == "Renewable":
                    renewable_data.append(energy_record)
                else:
                    non_renewable_data.append(energy_record)
            else:
                other_data.append(energy_record)

        if sno in [3, 4, 5, 6]:
            return other_data, round(grand_total_gj, 3), round(grand_total_kwh, 3)
        else:
            return (
                renewable_data,
                non_renewable_data,
                round(grand_total_renewable_gj, 3),
                round(grand_total_non_renewable_gj, 3),
            )

    def set_locations_data(self):
        """
        If Organisation is given and Corporate and Location is not given, then get all corporate locations
        If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
        If Location is given, then get only that location
        """
        if self.organisation and self.corporate and self.location:
            self.locations = Location.objects.filter(id=self.location.id)
        elif (
            self.organisation is None and self.corporate and self.location is None
        ) or (self.organisation and self.corporate and self.location is None):
            self.corporates = Corporateentity.objects.filter(id=self.corporate.id)
            self.locations = Location.objects.filter(
                corporateentity__in=self.corporates
            )
        elif self.organisation and self.corporate is None and self.location is None:
            self.organisations = Organization.objects.filter(id=self.organisation.id)
            self.corporates = Corporateentity.objects.filter(
                organization__in=self.organisations
            )
            self.locations = Location.objects.filter(
                corporateentity__in=self.corporates
            )
        else:
            raise serializers.ValidationError(
                "Not send any of the following fields: organisation, corporate, location"
            )

    def get(self, request):

        try:

            serializer = CheckAnalysisViewSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            self.from_date = serializer.validated_data["start"]
            self.to_date = serializer.validated_data["end"]

            self.organisation = serializer.validated_data["organisation"]
            self.corporate = serializer.validated_data.get("corporate", None)
            self.location = serializer.validated_data.get("location", None)

            self.clients_id = request.user.client.id
            # * Set Locations Queryset
            self.set_locations_data()

            response_data = {}
            (
                consumed_renewable,
                consumed_non_renewable,
                consumed_total_renewable_gj,
                consumed_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1c-1e-consumed_fuel", sno=1
            )
            response_data["fuel_consumption_from_renewable"] = consumed_renewable
            response_data["fuel_consumption_from_non_renewable"] = (
                consumed_non_renewable
            )
            if consumed_renewable:
                response_data["fuel_consumption_from_renewable"].append(
                    {
                        "Total": consumed_total_renewable_gj,
                        "Unit": "GJ",
                    }
                )
            if consumed_non_renewable:
                response_data["fuel_consumption_from_non_renewable"].append(
                    {
                        "Total": consumed_total_non_renewable_gj,
                        "Unit": "GJ",
                    }
                )

            (
                direct_renewable,
                direct_non_renewable,
                direct_total_renewable_gj,
                direct_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1a-1b-direct_purchased", sno=7
            )
            response_data["direct_purchased_from_renewable"] = direct_renewable
            response_data["direct_purchased_from_non_renewable"] = direct_non_renewable
            if direct_renewable:
                response_data["direct_purchased_from_renewable"].append(
                    {
                        "Total": direct_total_renewable_gj,
                        "Unit": "GJ",
                    }
                )
            if direct_non_renewable:
                response_data["direct_purchased_from_non_renewable"].append(
                    {
                        "Total": direct_total_non_renewable_gj,
                        "Unit": "GJ",
                    }
                )

            (
                self_generated_renewable,
                self_generated_non_renewable,
                self_generated_total_renewable_gj,
                self_generated_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1-self_generated", sno=1
            )
            response_data["self_generated_from_renewable"] = self_generated_renewable
            response_data["self_generated_from_non_renewable"] = (
                self_generated_non_renewable
            )
            if self_generated_renewable:
                response_data["self_generated_from_renewable"].append(
                    {
                        "Total": self_generated_total_renewable_gj,
                        "Unit": "GJ",
                    }
                )
            if self_generated_non_renewable:
                response_data["self_generated_from_non_renewable"].append(
                    {
                        "Total": self_generated_total_non_renewable_gj,
                        "Unit": "GJ",
                    }
                )

            (
                energy_sold_renewable,
                energy_sold_non_renewable,
                energy_sold_total_renewable_gj,
                energy_sold_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1d-energy_sold", sno=2
            )
            response_data["energy_sold_from_renewable"] = energy_sold_renewable
            response_data["energy_sold_from_non_renewable"] = energy_sold_non_renewable
            if energy_sold_renewable:
                response_data["energy_sold_from_renewable"].append(
                    {
                        "Total": energy_sold_total_renewable_gj,
                        "Unit": "GJ",
                    }
                )
            if energy_sold_non_renewable:
                response_data["energy_sold_from_non_renewable"].append(
                    {
                        "Total": energy_sold_total_non_renewable_gj,
                        "Unit": "GJ",
                    }
                )

            outside_org_data, outside_org_total_gj, outside_org_total_kwh = (
                self.process_energy_data(
                    path="gri-environment-energy-302-2a-energy_consumption_outside_organization",
                    sno=3,
                )
            )
            response_data["energy_consumption_outside_the_org"] = outside_org_data
            if outside_org_data:
                response_data["energy_consumption_outside_the_org"].append(
                    {"Total": outside_org_total_gj, "Unit": "GJ"}
                )

            energy_consumption_within_the_org = [
                {
                    "type_of_energy_consumed": "Non-renewable fuel consumed",
                    "consumption": consumed_total_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Renewable fuel consumed",
                    "consumption": consumed_total_non_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam purchased for consumption from renewable sources.",
                    "consumption": direct_total_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources.",
                    "consumption": direct_total_non_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed  from renewable source",
                    "consumption": self_generated_total_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed  from non-renewable source",
                    "consumption": self_generated_total_non_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (renewable energy)",
                    "consumption": energy_sold_total_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (non-renewable energy)",
                    "consumption": energy_sold_total_non_renewable_gj,
                    "unit": "GJ",
                },
                {
                    "Total": round(
                        consumed_total_renewable_gj
                        + consumed_total_non_renewable_gj
                        + direct_total_renewable_gj
                        + direct_total_non_renewable_gj
                        + self_generated_total_renewable_gj
                        + self_generated_total_non_renewable_gj
                        - energy_sold_total_renewable_gj
                        - energy_sold_total_non_renewable_gj,
                        3,
                    ),
                    "unit": "GJ",
                },
            ]

            response_data["energy_consumption_within_the_org"] = (
                energy_consumption_within_the_org
            )

            k = response_data["energy_consumption_within_the_org"][-1]["Total"]

            if k != 0:
                response_data["energy_consumption_within_the_org"] = (
                    energy_consumption_within_the_org
                )
            else:
                response_data["energy_consumption_within_the_org"] = []

            energy_intensity_data, _, _ = self.process_energy_data(
                path="gri-environment-energy-302-3a-3b-3c-3d-energy_intensity",
                sno=6,
                total_energy_consumption_within_org=k,
            )

            if energy_intensity_data:
                response_data["energy_intensity"] = energy_intensity_data
            else:
                response_data["energy_intensity"] = []

            reduction_energy_data, reduction_total_gj, reduction_total_kwh = (
                self.process_energy_data(
                    path="gri-environment-energy-302-4a-4b-reduction_of_energy_consumption",
                    sno=4,
                )
            )
            response_data["reduction_of_ene_consump"] = reduction_energy_data
            if reduction_energy_data:
                response_data["reduction_of_ene_consump"].append(
                    {
                        "Total1": reduction_total_gj,
                        "Unit1": "GJ",
                        "Total2": reduction_total_kwh,
                        "Unit2": "KWh",
                    }
                )

            (
                reduction_products_data,
                reduction_products_total_gj,
                reduction_products_total_kwh,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-5a-5b-reduction_in_energy_in_products_and_servies",
                sno=5,
            )
            response_data["reduction_of_ene_prod_and_services"] = (
                reduction_products_data
            )
            if reduction_products_data:
                response_data["reduction_of_ene_prod_and_services"].append(
                    {
                        "Total1": reduction_products_total_gj,
                        "Unit1": "GJ",
                        "Total2": reduction_products_total_kwh,
                        "Unit2": "KWh",
                    }
                )

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
