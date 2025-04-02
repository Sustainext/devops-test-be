from rest_framework.views import APIView
from rest_framework.response import Response
from datametric.models import EmissionAnalysis
from ..models import Scenerio


class FetchEmissionData(APIView):
    def get_scenario_data(self, scenario_id):
        # Fetch scenario data from the database
        scenario_data = Scenerio.objects.get(id=scenario_id)
        return scenario_data

    def get(self, request, scenario_id):
        try:
            scenario_data = self.get_scenario_data(scenario_id)

            emission_data = EmissionAnalysis.objects.filter(
                year=scenario_data.base_year
            )
            response = []
            for data in emission_data:
                entry = {
                    "Scope": data.scope,
                    "Category": data.category,
                    "Sub-Category": data.subcategory,
                    "Region": data.region,
                }
                response.append(entry)

            return Response(response, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
