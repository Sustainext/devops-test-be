from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import copy
from django.shortcuts import get_object_or_404
from apps.optimize.models.OptimizeScenario import Scenerio
from apps.optimize.models.SelectedActivityModel import SelectedActivity
from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.BusinessMetric import BusinessMetric
from collections import defaultdict
from apps.optimize.filters import CalculatedResultFilter


class CompareScenariosAPIView(APIView):
    def get_year_map_data(self, results, business_metric, selected_activities):
        year_map = defaultdict(list)

        activity_map = {str(act.uuid): act for act in selected_activities}

        for res in results:
            year = str(res.year)
            metric = res.metric
            weightage_key = f"{metric}_weightage"
            weightage = getattr(business_metric, weightage_key, 0)
            value = round(res.result.get("co2e", 0) / 1000, 4) * weightage  # Tonnes

            uuid_str = str(res.uuid)
            selected_activity = activity_map.get(uuid_str)
            decarbonization = False

            if selected_activity:
                pc = selected_activity.percentage_change or {}
                ca = selected_activity.changes_in_activity or {}
                year_str = str(year)

                if year_str in pc and pc[year_str]:
                    decarbonization = True
                elif (
                    year_str in ca
                    and isinstance(ca[year_str], dict)
                    and ca[year_str].get("activity_id")
                    and res.activity_id != ca[year_str]["activity_id"]
                ):
                    decarbonization = True

            existing = next((r for r in year_map[year] if r["uuid"] == uuid_str), None)
            if existing:
                existing[metric] = value
                existing["decarbonization"] = (
                    existing["decarbonization"] or decarbonization
                )
            else:
                year_map[year].append(
                    {
                        "uuid": uuid_str,
                        "scope": res.scope,
                        "category": res.category,
                        "sub_category": res.sub_category,
                        "activity_name": res.activity_name,
                        "activity_id": res.activity_id,
                        metric: value,
                        "decarbonization": decarbonization,
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
            selected_activities = SelectedActivity.objects.filter(scenario=scenario)
            business_metric = get_object_or_404(BusinessMetric, scenario=scenario)

            queryset = CalculatedResult.objects.filter(scenario=scenario)

            # Apply filters dynamically
            filtered_qs = CalculatedResultFilter(
                filters, queryset=queryset
            ).qs.order_by("year", "metric")

            year_map = self.get_year_map_data(
                filtered_qs, business_metric, selected_activities
            )
            totals = self.add_total_dict(year_map, filtered_qs)
            base_year_unselected_data = self.get_base_year_unselected_data(
                year_map, selected_activities, scenario.base_year
            )
            excluded_totals = self.add_total_dict(
                base_year_unselected_data, filtered_qs
            )

            base_year_str = str(scenario.base_year)
            excluded_values = excluded_totals.get(base_year_str, {})

            for year, metrics_dict in totals.items():
                if year == base_year_str:
                    continue
                for metric, value in excluded_values.items():
                    metrics_dict[metric] += value

            response_data[scenario_id] = {
                "metadata": {
                    "unit": "t",
                    "baseYear": scenario.base_year,
                    "targetYear": scenario.target_year,
                    "years": [
                        str(y)
                        for y in range(scenario.base_year, scenario.target_year + 1)
                    ],
                },
                "totals": totals,
                "yearly_data": year_map,
            }

        return Response(response_data)
