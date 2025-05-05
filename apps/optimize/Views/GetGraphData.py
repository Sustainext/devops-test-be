from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.OptimizeScenario import Scenerio
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class GetGraphData(APIView):
    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        results = CalculatedResult.objects.filter(scenario=scenario).order_by(
            "year", "metric"
        )

        year_map = {}
        for res in results:
            year = str(res.year)
            if year not in year_map:
                year_map[year] = []

            # Try to merge same activity + year across metrics
            existing = next(
                (r for r in year_map[year] if r["activity_name"] == res.activity_name),
                None,
            )
            if existing:
                existing[res.metric] = res.result
            else:
                year_map[year].append(
                    {
                        "activity_name": res.activity_name,
                        res.metric: res.result,
                    }
                )

        return Response(year_map)
