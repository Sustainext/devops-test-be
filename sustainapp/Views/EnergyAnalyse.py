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


class EnergyAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def process_energy_data(self, path, sno, total_energy_consumption_within_org=None):
        conversions = {
            "Joules": {"GJ": 1e-9, "kWh": 0.00000027778},
            "KJ": {"GJ": 1e-6, "kWh": 0.00027778},
            "Wh": {"GJ": 0.0000036, "kWh": 0.001},
            "KWh": {"GJ": 0.0036, "kWh": 1},
            "GJ": {"GJ": 1, "kWh": 277.78},
            "MMBtu": {"GJ": 1.055056, "kWh": 293.071},
        }

        consumed_ene_query = RawResponse.objects.filter(
            location__in=self.locations.values_list("name", flat=True),
            year__range=(self.from_date.year, self.to_date.year),
            month__range=(self.from_date.month, self.to_date.month),
            path__slug=path,
        )

        if not consumed_ene_query : 
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
            quantity = float(item[quantity_key])
            unit = item[unit_key]
            return (
                conversions[unit]["GJ"] * quantity,
                conversions[unit]["kWh"] * quantity,
            )

        key_generators = {
            1: lambda item: (item["EnergyType"], item["Source"], item["Renewable"]),
            2: lambda item: (
                item["EnergyType"],
                item["Source"],
                item["Typeofentity"],
                item["Nameofentity"],
                item["Renewable"],
            ),
            3: lambda item: (item["EnergyType"], item["Purpose"]),
            4: lambda item: (
                item["Typeofintervention"],
                item["Energytypereduced"],
                item["Energyreductionis"],
                item["Baseyear"],
                item["Methodologyused"],
            ),
            5: lambda item: item["ProductServices"],
            6: lambda item: (item["Organizationmetric"], item["Metricunit"]),
        }

        for item in data:
            try:
                if sno < 4:
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
                    if sno in [1, 2]:
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
                "Quantity_GJ": round(total, 3),
                "Units_GJ": "GJ",
            },
            2: lambda key, total: {
                "Energy_type": key[0],
                "Source": key[1],
                "Entity_type": key[2],
                "Entity_name": key[3],
                "Quantity_GJ": round(total, 3),
                "Units_GJ": "GJ",
            },
            3: lambda key, total: {
                "Energy_type": key[0],
                "Purpose": key[1],
                "Quantity_GJ": round(total, 3),
                "Units_GJ": "GJ",
            },
            4: lambda key, total: {
                "Type_of_intervention": key[0],
                "Energy_type": key[1],
                "Energy_reduction": key[2],
                "Base_year": key[3],
                "Methodology": key[4],
                "Quantity_GJ": round(total, 3),
                "Units_GJ": "GJ",
                "Quantity_kWh": round(total * 277.78, 3),
                "Units_kWh": "kWh",
            },
            5: lambda key, total: {
                "Product": key,
                "Quantity_GJ": round(total, 3),
                "Units_GJ": "GJ",
                "Quantity_kWh": round(total * 277.778, 3),
                "Units_kWh": "kWh",
            },
            6: lambda key, total: {
                "Energy_quantity": total_energy_consumption_within_org,
                "Organization_metric": key[0],
                "Energy_intensity": round(
                    total_energy_consumption_within_org / total["Metricquantity"], 2
                ),
                "Units_GJ": f"GJ/{key[1]}",
                "Energy_intensity_in_kWh": round(
                    total_energy_consumption_within_org
                    / total["Metricquantity"]
                    * 277.778,
                    3,
                ),
                "Units_kWh": f"kWh/{key[1]}",
            },
        }

        for key, total_quantity in grouped_data.items():
            energy_record = record_creators[sno](key, total_quantity)

            if sno in [1, 2]:
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
            response_data["fuel_consumption_from_non_renewable"] = consumed_non_renewable
            if consumed_renewable  :
                response_data["fuel_consumption_from_renewable"].append({
                    "Total_GJ": consumed_total_renewable_gj,
                    "Units": "GJ",})
            if  consumed_non_renewable :
                response_data["fuel_consumption_from_non_renewable"].append({
                    "Total_GJ": consumed_total_non_renewable_gj,
                    "Units": "GJ",})

            (
                direct_renewable,
                direct_non_renewable,
                direct_total_renewable_gj,
                direct_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1a-1b-direct_purchased", sno=1
            )
            response_data["direct_purchased_from_renewable"]= direct_renewable
            response_data["direct_purchased_from_non_renewable"] = direct_non_renewable
            if direct_renewable :
                response_data["direct_purchased_from_renewable"].append({
                    "Total_GJ": direct_total_renewable_gj,
                    "Units": "GJ",})
            if  direct_non_renewable:
                response_data["direct_purchased_from_non_renewable"].append({
                    "Total_GJ": direct_total_non_renewable_gj,
                    "Units": "GJ",})

            (
                self_generated_renewable,
                self_generated_non_renewable,
                self_generated_total_renewable_gj,
                self_generated_total_non_renewable_gj,
            ) = self.process_energy_data(
                path="gri-environment-energy-302-1-self_generated", sno=1
            )
            response_data["self_generated_from_renewable"] = self_generated_renewable
            response_data["self_generated_from_non_renewable"] = self_generated_non_renewable
            if self_generated_renewable:
                response_data["self_generated_from_renewable"].append({
                    "Total_GJ": self_generated_total_renewable_gj,
                    "Units": "GJ",
                })
            if  self_generated_non_renewable:
                response_data["self_generated_from_non_renewable"].append({
                    "Total_GJ": self_generated_total_non_renewable_gj,
                    "Units": "GJ",
                })

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
                response_data["energy_sold_from_renewable"].append({
                    "Total_GJ": energy_sold_total_renewable_gj,
                    "Units": "GJ",
                })
            if  energy_sold_non_renewable:
                response_data["energy_sold_from_non_renewable"].append({
                    "Total_GJ": energy_sold_total_non_renewable_gj,
                    "Units": "GJ",
                })

            outside_org_data, outside_org_total_gj, outside_org_total_kwh = (
                self.process_energy_data(
                    path="gri-environment-energy-302-2a-energy_consumption_outside_organization",
                    sno=3,
                )
            )
            response_data["energy_consumption_outside_the_org"] = outside_org_data
            if outside_org_data:
                response_data["energy_consumption_outside_the_org"].append(
                    {"Total_GJ": outside_org_total_gj, "Units_GJ": "GJ"}
                )

            energy_consumption_within_the_org = [
                {
                    "type_of_energy_consumed": "Non-renewable fuel consumed",
                    "consumption": consumed_total_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Renewable fuel consumed",
                    "consumption": consumed_total_non_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam purchased for consumption from renewable sources.",
                    "consumption": direct_total_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources.",
                    "consumption":direct_total_non_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed  from renewable source",
                    "consumption":self_generated_total_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed  from non-renewable source",
                    "consumption": self_generated_total_non_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (renewable energy)",
                    "consumption": energy_sold_total_renewable_gj,
                    "units": "GJ",
                },
                {
                    "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (non-renewable energy)",
                    "consumption": energy_sold_total_non_renewable_gj,
                    "units": "GJ",
                },
                {
                    "Total": round(consumed_total_renewable_gj + consumed_total_non_renewable_gj + direct_total_renewable_gj + direct_total_non_renewable_gj + self_generated_total_renewable_gj + self_generated_total_non_renewable_gj  + energy_sold_total_renewable_gj + energy_sold_total_non_renewable_gj, 3,),
                    "units": "GJ",
                }
            ]
            response_data["energy_consumption_within_the_org"] = (
                energy_consumption_within_the_org
            )

            k = response_data["energy_consumption_within_the_org"][-1]["Total"]

            energy_intensity_data, _, _ = self.process_energy_data(
                path="gri-environment-energy-302-3a-3b-3c-3d-energy_intensity",
                sno=6,
                total_energy_consumption_within_org=k,
            )

            if energy_intensity_data:
                response_data["energy_intensity"] = energy_intensity_data   
            else : response_data["energy_intensity"] = []

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
                        "Total_GJ": reduction_total_gj,
                        "Units_GJ": "GJ",
                        "Total_KWh": reduction_total_kwh,
                        "Units_KWh": "KWh",
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
            response_data["reduction_of_ene_prod_&_services"] = reduction_products_data
            if reduction_products_data:
                response_data["reduction_of_ene_prod_&_services"].append(
                    {
                        "Total_GJ": reduction_products_total_gj,
                        "Units_GJ": "GJ",
                        "Total_KWh": reduction_products_total_kwh,
                        "Units_KWh": "KWh",
                    }
                )

            
            final_response = {
                "fuel_consumption_from_renewable": response_data["fuel_consumption_from_renewable"],
                "fuel_consumption_from_non_renewable": response_data["fuel_consumption_from_non_renewable"],
                "energy_consumption_within_the_org" : response_data["energy_consumption_within_the_org"],
                "direct_purchased_from_renewable" : response_data["direct_purchased_from_renewable"],
                "direct_purchased_from_non_renewable ": response_data["direct_purchased_from_non_renewable"],
                "self_generated_from_renewable" : response_data["self_generated_from_renewable"],
                "self_generated_from_non_renewable" : response_data["self_generated_from_non_renewable"],
                "energy_sold_from_renewable" : response_data["energy_sold_from_renewable"],
                "energy_sold_from_non_renewable" : response_data["energy_sold_from_non_renewable"],
                "energy_consumption_outside_the_org" : response_data["energy_consumption_outside_the_org"],
                "energy_intensity" : response_data["energy_intensity"],
                "reduction_of_ene_consump" : response_data["reduction_of_ene_consump"],
                "reduction_of_ene_prod_&_services" : response_data["reduction_of_ene_prod_&_services"],
            }
            

            return Response(final_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
