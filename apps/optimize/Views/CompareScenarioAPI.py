from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.optimize.models.OptimizeScenario import Scenerio
from apps.optimize.Service.scenario_graph_data import ScenarioGraphService


class CompareScenariosAPIView(APIView):
    def post(self, request):
        scenario_requests = request.data.get("scenarios", [])
        if not scenario_requests:
            return Response(
                {"error": "No scenarios provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {}

        for scenario_info in scenario_requests:
            scenario_id = scenario_info.get("id")
            filters = scenario_info.get("filters", {})

            scenario = get_object_or_404(Scenerio, id=scenario_id)
            service = ScenarioGraphService(scenario, filters)
            response_data[scenario_id] = service.build_response()

        return Response(response_data)
