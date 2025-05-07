from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.OptimizeScenario import Scenerio
from apps.optimize.models.SelectedActivityModel import SelectedActivity
from apps.optimize.models.BusinessMetric import BusinessMetric
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from collections import defaultdict
import copy


class GetGraphData(APIView):
    def get_year_map_data(self, results, business_metric):
        year_map = defaultdict(list)

        for res in results:
            year = str(res.year)
            metric = res.metric
            weightage_key = f"{metric}_weightage"
            weightage = getattr(business_metric, weightage_key, 0)
            value = round(
                res.result.get("co2e", 0) / 1000, 4
            )  # Converting co2e to tonnes
            value = value * weightage

            existing = next(
                (r for r in year_map[year] if r["uuid"] == str(res.uuid)), None
            )

            if existing:
                existing[metric] = value
            else:
                year_map[year].append(
                    {
                        "uuid": str(res.uuid),
                        "scope": res.scope,
                        "category": res.category,
                        "sub_category": res.sub_category,
                        "activity_name": res.activity_name,
                        "activity_id": res.activity_id,
                        metric: value,
                    }
                )
        return year_map

    def add_total_dict(self, year_data, results):
        totals = defaultdict(lambda: defaultdict(float))
        metrics = set([res.metric for res in results])

        for year, data in year_data.items():
            for entry in data:
                # For each metric in the metrics list, dynamically sum the values
                for metric in metrics:
                    if metric in entry:  # Check if the metric exists in the entry
                        totals[year][metric] += entry[metric]

        final_totals = {}
        for year, metric_totals in totals.items():
            year_total = sum(metric_totals.values())
            metric_totals["total"] = year_total
            final_totals[year] = dict(metric_totals)

        return final_totals

    def get_base_year_unselected_data(self, year_map, selected_activities, base_year):
        selected_keys = {str(sa.uuid) for sa in selected_activities}

        base_year_data = copy.deepcopy(year_map.get(str(base_year), []))

        # Filter out any entry that matches a selected key
        filtered = [
            entry for entry in base_year_data if entry["uuid"] not in selected_keys
        ]
        result = {base_year: filtered}
        return result

    def get(self, request, scenario_id):
        scenario = get_object_or_404(Scenerio, id=scenario_id)
        selected_activities = SelectedActivity.objects.filter(scenario=scenario)
        business_metric = get_object_or_404(BusinessMetric, scenario=scenario)
        results = CalculatedResult.objects.filter(scenario=scenario).order_by(
            "year", "metric"
        )
        year_map = self.get_year_map_data(results, business_metric)
        totals = self.add_total_dict(year_map, results)
        base_year_unselected_data = self.get_base_year_unselected_data(
            year_map, selected_activities, scenario.base_year
        )
        excluded_totals = self.add_total_dict(base_year_unselected_data, results)

        # Add Excluded total to other years except base year
        base_year_str = scenario.base_year
        excluded_values = excluded_totals.get(base_year_str, {})

        # Update each year (except base year) entries with excluded totals
        for year, dict in totals.items():
            if year == str(base_year_str):
                continue  # skip base year
            for metric, value in excluded_values.items():
                dict[metric] += value

        response_data = {
            "metadata": {
                "unit": "t",
                "baseYear": scenario.base_year,
                "targetYear": scenario.target_year,
                "years": [
                    str(y) for y in range(scenario.base_year, scenario.target_year + 1)
                ],
            },
            "totals": totals,
            "yearly_data": year_map,
            "base_year_excluding_selected": base_year_unselected_data,
            "excluded_totals": excluded_totals.values(),
        }

        return Response(response_data)
