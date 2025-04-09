from rest_framework.views import APIView
from rest_framework.response import Response
from datametric.models import EmissionAnalysis
from ..models import Scenerio
from sustainapp.models import Location


class EmissionDataExistsView(APIView):
    def get_scenario_data(self, scenario_id):
        # Fetch scenario data from the database
        scenario_data = Scenerio.objects.get(id=scenario_id)
        return scenario_data

    def get(self, request, scenario_id):
        scenario = self.get_scenario_data(scenario_id)
        if scenario.scenario_by == "organization":
            locations = Location.objects.filter(
                corporateentity__organization=scenario.organization
            ).values_list("id", flat=True)

            emission_data = EmissionAnalysis.objects.filter(
                year=scenario.base_year,
                raw_response__locale__in=locations,
            ).exists()

            return Response({"exists": emission_data})

        elif scenario.scenario_by == "corporate":
            locations = Location.objects.filter(corporateentity=scenario.corporate)

            emission_data = EmissionAnalysis.objects.filter(
                year=scenario.base_year,
                raw_response__locale__in=locations,
            ).exists()

            return Response({"exists": emission_data})

        else:
            return Response({"exists": False})
