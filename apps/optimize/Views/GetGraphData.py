from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.OptimizeScenario import Scenerio
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.optimize.filters import CalculatedResultFilter
from apps.optimize.Service.scenario_graph_data import ScenarioGraphService


class GetGraphData(GenericAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = CalculatedResultFilter

    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        filtered_results = self.filter_queryset(
            CalculatedResult.objects.filter(scenario=scenario).order_by(
                "year", "metric"
            )
        )

        service = ScenarioGraphService(scenario=scenario)
        response_data = service.single_scenario_response(filtered_results)

        return Response(response_data)
