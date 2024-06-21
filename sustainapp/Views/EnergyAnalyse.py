from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisEnergySerializer import AnalyzeEnergySerializer



class EnergyAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def process_energy_data(self,filter1,filter2,renewability,path_id):
        
        conversions = {
            "J": {"GJ": 1e-9, "kWh": 0.00000027778},
            "KJ": {"GJ": 1e-6, "kWh": 0.00027778},
            "Wh": {"GJ": 0.0000036, "kWh": 0.001},
            "KWh": {"GJ": 0.0036, "kWh": 1},
            "GJ": {"GJ": 1, "kWh": 277.78},
            "MMBtu": {"GJ": 1.055056, "kWh": 293.071},
        }

        if self.location and self.corporate and self.organization :
            query = DataPoint.objects.filter(location=self.location.name, year_in=range(self.from_year,self.to_year), month_in=range(self.from_month,self.to_month), path=path_id, metric_name='Energy_Type')
        elif self.corporate and self.organization :
            query = DataPoint.objects.filter(location=self.corporate.location.name, year_in=range(self.from_year,self.to_year), month_in=range(self.from_month,self.to_month), path=path_id, metric_name='Energy_Type')
        else :
            query = DataPoint.objects.filter(location=self.organization.corporate.location.name, year_in=range(self.from_year,self.to_year), month_in=range(self.from_month,self.to_month), path=path_id, metric_name='Energy_Type')
        # if renewability:
        #     query = query.filter(renewability=renewability)




    def get(self, request ):

        serializer = AnalyzeEnergySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        self.from_date = serializer.validated_data.get("from_date")
        self.to_date = serializer.validated_data.get("to_date")
        try:
            self.from_date_obj = datetime.strptime(self.from_date, "%Y-%m-%d").date()  # Assuming format YYYY-MM-DD
            self.to_date_obj = datetime.strptime(self.to_date, "%Y-%m-%d").date()  # Assuming format YYYY-MM-DD
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.from_month, self.from_year = self.from_date_obj.month, self.from_date_obj.year
        self.to_month, self.to_year = self.to_date_obj.month, self.to_date_obj.year

        self.organization = serializer.validated_data.get("organization")
        self.corporate = serializer.validated_data.get("corporate", None) 
        self.location = serializer.validated_data.get("location", None) 

        response_data = {
            "energy_consumption_within_the_org": {
                    "Non-renewable fuel consumed": 0,
                    "Renewable fuel consumed": 0,
                    "Electricity, heating, cooling, and steam purchased for consumption from renewable sources": 0,
                    "Electricity, heating, cooling, and steam purchased for consumption from non-renewable sources": 0,
                    "Self-generated electricity, heating, cooling, and steam, which are not consumed from renewable source": 0,
                    "Self-generated electricity, heating, cooling, and steam, which are not consumed from non-renewable source": 0,
                    "Electricity, heating, cooling, and steam sold (renewable energy)": 0,
                    "Electricity, heating, cooling, and steam sold (non-renewable energy)": 0,
                    "Total Energy consumption within the org": 0,
                }
        }

        response_data["fuel_consume_within_org_rene"] = self.process_energy_data(filter1="EnergyType",filter2="source"renewability="Renewable",path=5)


