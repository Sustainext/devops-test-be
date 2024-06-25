from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisEnergySerializer import AnalyzeEnergySerializer
from sustainapp.Serializers.CheckAnalysisViewSerializer import CheckAnalysisViewSerializer

from django.db.models import Prefetch
from rest_framework import serializers

class EnergyAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def process_energy_data(self, path, sno, total_energy_consumption_within_org=None ):

        conversions = {
            "Joules": {"GJ": 1e-9, "kWh": 0.00000027778},
            "KJ": {"GJ": 1e-6, "kWh": 0.00027778},
            "Wh": {"GJ": 0.0000036, "kWh": 0.001},
            "KWh": {"GJ": 0.0036, "kWh": 1},
            "GJ": {"GJ": 1, "kWh": 277.78},
            "MMBtu": {"GJ": 1.055056, "kWh": 293.071},
        }
        consumed_ene_query = RawResponse.objects.filter(location__in=self.locations.values_list("name",flat=True), year__range=(self.from_date.year,self.to_date.year), month__range=(self.from_date.month,self.to_date.month), path__slug=path)
        data = []
        for obj in consumed_ene_query:
            data.extend(obj.data)

        grouped_data = {}
        grand_total_renewable_gj = 0
        grand_total_non_renewable_gj = 0
        grand_total_gj = 0
        grand_total_kwh = 0
        
        for item in data:
            try :
                if sno < 4:
                    quantity = float(item["Quantity"])
                    unit = item["Unit"]
                    
                    quantity_in_gj = conversions[unit]["GJ"] * quantity
                    # quantity_in_kwh = conversions[unit]["kWh"] * quantity
                elif sno == 4 : 
                    quantity = float(item["Quantitysavedduetointervention"])
                    unit = item["Unit"]
                    quantity_in_gj = conversions[unit]["GJ"] * quantity
                    quantity_in_kwh = conversions[unit]["kWh"] * quantity
                elif sno == 5:
                    quantity = float(item["Quantity"])
                    unit = item["Unit"]
                    quantity_in_gj = conversions[unit]["GJ"] * quantity
                    quantity_in_kwh = conversions[unit]["kWh"] * quantity
                elif sno == 6 :
                    organization_metric = item["Organizationmetric"]
                    metric_quantity = float(item["Metricquantity"])
                    metric_unit = item["Metricunit"]
                    key = (organization_metric, metric_unit)
                    if key not in grouped_data:
                        grouped_data[key] = {"Metricquantity": 0}
                    grouped_data[key]["Metricquantity"] += metric_quantity
                    continue
                
                if sno == 1 :
                    energy_type = item["EnergyType"]
                    source = item["Source"]
                    renewable_status = item["Renewable"]
                    key = (energy_type, source, renewable_status)
                elif sno == 2 :
                    energy_type = item["EnergyType"]
                    source = item["Source"]
                    entity_type = item["Typeofentity"]
                    entity_name = item["Nameofentity"]
                    renewable_status = item["Renewable"]
                    key = (energy_type, source, entity_type, entity_name, renewable_status)
                elif sno == 3 :
                    energy_type = item["EnergyType"]
                    purpose = item["Purpose"]
                    key = (energy_type, purpose)
                elif sno == 4 :
                    type_of_intervention = item["Typeofintervention"]
                    energy_type = item["Energytypereduced"]
                    energy_reduction = item["Energyreductionis"]
                    base_year = item["Baseyear"]
                    methodology = item["Methodologyused"]
                    key = (type_of_intervention,energy_type, energy_reduction,base_year, methodology)
                elif sno == 5 :
                    product = item["ProductServices"]
                    key = (product)


                if key not in grouped_data:
                    grouped_data[key] = 0
                
                grouped_data[key] += quantity_in_gj

                if sno in [4, 5]:
                    grand_total_gj += quantity_in_gj
                    grand_total_kwh += quantity_in_kwh
                else:
                    if sno in [1, 2]:
                        if renewable_status == "Renewable":
                            grand_total_renewable_gj += quantity_in_gj
                        else:
                            grand_total_non_renewable_gj += quantity_in_gj
                    else:
                        grand_total_gj += quantity_in_gj
            except KeyError as e :
                print(f"Missing field {e} in data item, skipping this item.")
                continue

        renewable_data = []
        non_renewable_data = []
        other_data = []
        
        for key, total_quantity in grouped_data.items():
            if sno == 1 :
                energy_type, source, renewable_status = key
                energy_record = {
                    "Energy_type": energy_type,
                    "Source": source,
                    "Quantity_GJ":  round(total_quantity, 2),  #total_quantity,
                    "Units_GJ": "GJ"
                }
            elif sno == 2 :
                energy_type, source, entity_type, entity_name, renewable_status = key
                energy_record = {
                    "Energy_type": energy_type,
                    "Source": source,
                    "Entity_type": entity_type,
                    "Entity_name": entity_name,
                    "Quantity_GJ":  round(total_quantity, 2),  #total_quantity,
                    "Units_GJ": "GJ"
                }
            elif sno == 3:
                energy_type, purpose = key
                energy_record = {
                    "Energy_type": energy_type,
                    "Purpose": purpose,
                    "Quantity_GJ":  round(total_quantity, 2),  #total_quantity,
                    "Units_GJ": "GJ"
                }
            if sno == 4:
                    type_of_intervention, energy_type, energy_reduction, base_year, methodology = key
                    energy_record = {
                        "Type_of_intervention": type_of_intervention,
                        "Energy_type": energy_type,
                        "Energy_reduction": energy_reduction,
                        "Base_year": base_year,
                        "Methodology": methodology,
                        "Quantity_GJ":  round(total_quantity, 2),  #total_quantity,
                        "Units_GJ": "GJ",
                        "Quantity_kWh": round(total_quantity * 277.78, 2),
                        "Units_kWh": "kWh"
                    }
            if sno == 5:
                product = key
                energy_record = {
                    "Product": product,
                    "Quantity_GJ":  round(total_quantity, 2),  #total_quantity,
                    "Units_GJ": "GJ",
                    "Quantity_kWh":  round(total_quantity*277.778, 2),   #total_quantity * 277.778,
                    "Units_kWh": "kWh"
                }
            if sno == 6 : 
                organization_metric, metric_unit = key
                metric_quantity = total_quantity["Metricquantity"]
                energy_intensity_gj = round(total_energy_consumption_within_org / metric_quantity, 2)
                energy_intensity_kwh =round(energy_intensity_gj * 277.778, 2)
                energy_record = {
                    "Energy_quantity": total_energy_consumption_within_org,
                    "Organization_metric": organization_metric,
                    "Energy_intensity": energy_intensity_gj,
                    "Units_GJ": f"GJ/{metric_unit}",
                    "Energy_intensity_in_kwh": energy_intensity_kwh,
                    "Units_KWh": f"KWh/{metric_unit}"
                }

            if sno in [1,2] : 
                if renewable_status == "Renewable":
                    renewable_data.append(energy_record)
                else:
                    non_renewable_data.append(energy_record)
            else:
                other_data.append(energy_record)

        if sno in [3, 4, 5, 6]:
            return other_data, round(grand_total_gj,2) , round (grand_total_kwh,2)
        else:
            return renewable_data, non_renewable_data, round(grand_total_renewable_gj,2), round(grand_total_non_renewable_gj,2)

        
            

    def set_locations_data(self):
        """
        If Organisation is given and Corporate and Location is not given, then get all corporate locations
        If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
        If Location is given, then get only that location
        """
        if self.organisation and self.corporate and self.location:
            self.locations = Location.objects.filter(id=self.location.id)
        elif (self.organisation is None and self.corporate and self.location is None) or (self.organisation and self.corporate and self.location is None):
            self.corporates = Corporateentity.objects.filter(id=self.corporate.id)
            self.locations = Location.objects.filter(corporateentity__in=self.corporates)
        elif (self.organisation and self.corporate is None and self.location is None):
            self.organisations = Organization.objects.filter(id=self.organisation.id)
            self.corporates = Corporateentity.objects.filter(organization__in=self.organisations)
            self.locations = Location.objects.filter(corporateentity__in=self.corporates)
        else:
            raise serializers.ValidationError(
                "Not send any of the following fields: organisation, corporate, location"
            )


    def get(self, request ):

        try : 

            serializer = CheckAnalysisViewSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            self.from_date = serializer.validated_data.get("start")
            self.to_date = serializer.validated_data.get("end")

            self.organisation = serializer.validated_data.get("organisation")
            self.corporate = serializer.validated_data.get("corporate", None) 
            self.location = serializer.validated_data.get("location", None) 
            # * Set Locations Queryset
            self.set_locations_data()

            response_data = {                                                  
                "consumed_energy" : {},                                                 
                "direct_purchased" : {},
                "self_generated" : {},
                "energy_sold" : {},
                
            }
            consumed_renewable, consumed_non_renewable, consumed_total_renewable_gj, consumed_total_non_renewable_gj = self.process_energy_data(path="gri-environment-energy-302-1c-1e-consumed_fuel", sno=1)
            response_data["consumed_energy"]["Renewable fuel consumed"] = consumed_renewable
            response_data["consumed_energy"]["Non-Renewable fuel consumed"] = consumed_non_renewable
            response_data["consumed_energy"]["Grand_total_Renewable"] = {"Quantity": consumed_total_renewable_gj, "Units": "GJ"}
            response_data["consumed_energy"]["Grand_total_Non_Renewable"] = {"Quantity": consumed_total_non_renewable_gj, "Units": "GJ"}

            direct_renewable, direct_non_renewable, direct_total_renewable_gj, direct_total_non_renewable_gj = self.process_energy_data(path="gri-environment-energy-302-1a-1b-direct_purchased", sno=1)
            response_data["direct_purchased"]["Renewable fuel consumed"] = direct_renewable
            response_data["direct_purchased"]["Non-Renewable fuel consumed"] = direct_non_renewable
            response_data["direct_purchased"]["Grand_total_Renewable"] = {"Quantity": direct_total_renewable_gj, "Units": "GJ"}
            response_data["direct_purchased"]["Grand_total_Non_Renewable"] = {"Quantity": direct_total_non_renewable_gj, "Units": "GJ"}

            self_generated_renewable, self_generated_non_renewable, self_generated_total_renewable_gj, self_generated_total_non_renewable_gj = self.process_energy_data(path="gri-environment-energy-302-1-self_generated", sno=1)
            response_data["self_generated"]["Renewable fuel consumed"] = self_generated_renewable
            response_data["self_generated"]["Non-Renewable fuel consumed"] = self_generated_non_renewable
            response_data["self_generated"]["Grand_total_Renewable"] = {"Quantity": self_generated_total_renewable_gj, "Units": "GJ"}
            response_data["self_generated"]["Grand_total_Non_Renewable"] = {"Quantity": self_generated_total_non_renewable_gj, "Units": "GJ"}

            energy_sold_renewable, energy_sold_non_renewable, energy_sold_total_renewable_gj, energy_sold_total_non_renewable_gj = self.process_energy_data(path="gri-environment-energy-302-1d-energy_sold", sno=2)
            response_data["energy_sold"]["Renewable fuel consumed"] = energy_sold_renewable
            response_data["energy_sold"]["Non-Renewable fuel consumed"] = energy_sold_non_renewable
            response_data["energy_sold"]["Grand_total_Renewable"] = {"Quantity": energy_sold_total_renewable_gj, "Units": "GJ"}
            response_data["energy_sold"]["Grand_total_Non_Renewable"] = {"Quantity": energy_sold_total_non_renewable_gj, "Units": "GJ"}

            outside_org_data, outside_org_total_gj, outside_org_total_kwh = self.process_energy_data(path="gri-environment-energy-302-2a-energy_consumption_outside_organization", sno=3)
            response_data["energy_consumption_outside_the_org"] = outside_org_data
            response_data["energy_consumption_outside_the_org"].append({"Grand_total_GJ": outside_org_total_gj, "Units_GJ": "GJ"})

            reduction_energy_data, reduction_total_gj, reduction_total_kwh = self.process_energy_data(path="gri-environment-energy-302-4a-4b-reduction_of_energy_consumption", sno=4)
            response_data["reduction_of_ene_consump"] = reduction_energy_data
            response_data["reduction_of_ene_consump"].append({"Grand_total_GJ": reduction_total_gj,  "Units_GJ": "GJ","Grand_total_kWh": reduction_total_kwh, "Units_KWh": "KWh"})

            reduction_products_data, reduction_products_total_gj, reduction_products_total_kwh = self.process_energy_data(path="gri-environment-energy-302-5a-5b-reduction_in_energy_in_products_and_servies", sno=5)
            response_data["reduction_of_ene_prod_&_services"] = reduction_products_data
            response_data["reduction_of_ene_prod_&_services"].append({"Grand_total_GJ": reduction_products_total_gj,  "Units_GJ": "GJ", "Grand_total_kWh": reduction_products_total_kwh, "Units_KWh": "KWh"})

            energy_consumption_within_the_org = [
                    {
                        "type_of_energy_consumed": "Non-renewable fuel consumed",
                        "consumption" : response_data["consumed_energy"]["Grand_total_Non_Renewable"]["Quantity"] ,
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Renewable_Fuel_Consumed",
                        "consumption" : response_data["consumed_energy"]["Grand_total_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (renewable energy)",
                        "consumption" : response_data["direct_purchased"]["Grand_total_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (non-renewable energy)",
                        "consumption" :  response_data["direct_purchased"]["Grand_total_Non_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (renewable energy)",
                        "consumption" : response_data["energy_sold"]["Grand_total_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Electricity, heating, cooling, and steam sold (non-renewable energy)",
                        "consumption" : response_data["energy_sold"]["Grand_total_Non_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed from renewable source",
                        "consumption" : response_data["self_generated"]["Grand_total_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "type_of_energy_consumed": "Self-generated electricity, heating, cooling, and steam, which are not consumed from non-renewable source",
                        "consumption" : response_data["self_generated"]["Grand_total_Non_Renewable"]["Quantity"],
                        "units" : "GJ"
                    },
                    {
                        "Total Energy Consumption Within the organization": round (response_data["consumed_energy"]["Grand_total_Non_Renewable"]["Quantity"] + response_data["consumed_energy"]["Grand_total_Renewable"]["Quantity"] + response_data["direct_purchased"]["Grand_total_Non_Renewable"]["Quantity"] + response_data["direct_purchased"]["Grand_total_Renewable"]["Quantity"] + response_data["energy_sold"]["Grand_total_Non_Renewable"]["Quantity"] + response_data["energy_sold"]["Grand_total_Renewable"]["Quantity"] + response_data["self_generated"]["Grand_total_Non_Renewable"]["Quantity"] + response_data["self_generated"]["Grand_total_Renewable"]["Quantity"], 2),
                        "units" : "GJ"
                    }
                ]
            response_data["energy_consumption_within_the_org"] = energy_consumption_within_the_org
            
            k= response_data["energy_consumption_within_the_org"][-1]["Total Energy Consumption Within the organization"]

            energy_intensity_data, _, _ = self.process_energy_data(path="gri-environment-energy-302-3a-3b-3c-3d-energy_intensity", sno=6,total_energy_consumption_within_org=k )

            response_data["energy_intensity"] = energy_intensity_data

            return Response(response_data, status=status.HTTP_200_OK)   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

