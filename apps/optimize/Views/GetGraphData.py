from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.OptimizeScenario import Scenerio
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from collections import defaultdict


class GetGraphData(APIView):
    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        results = CalculatedResult.objects.filter(scenario=scenario).order_by(
            "year", "metric"
        )

        year_map = defaultdict(list)
        totals = defaultdict(
            lambda: defaultdict(float)
        )  # totals[year][metric] = total_value

        for res in results:
            year = str(res.year)
            metric = res.metric
            value = float(res.result.get("co2e", 0))
            value = round((value / 1000), 2)  # converting to tonnes

            # Add to activity-wise map (optional for full detail)
            existing = next(
                (r for r in year_map[year] if r["activity_name"] == res.activity_name),
                None,
            )
            if existing:
                existing[metric] = value
            else:
                year_map[year].append(
                    {
                        "scope": res.scope,
                        "category": res.category,
                        "sub_category": res.sub_category,
                        "activity_name": res.activity_name,
                        "activity_id": res.activity_id,
                        metric: value,
                    }
                )

            # Accumulate totals per metric
            totals[year][metric] += value

        # Add "total" as sum of all metric values for each year
        formatted_totals = {}
        for year, metric_data in totals.items():
            year_total = sum(metric_data.values())
            metric_data["total"] = year_total
            formatted_totals[year] = {k: round(v, 2) for k, v in metric_data.items()}

        response_data = {
            "metadata": {
                "unit": "t",
                "baseYear": scenario.base_year,
                "targetYear": scenario.target_year,
                "years": [
                    str(y) for y in range(scenario.base_year, scenario.target_year + 1)
                ],
            },
            "totals": formatted_totals,
            "yearly_data": year_map,  # optional: remove if not needed
        }

        return Response(response_data)
