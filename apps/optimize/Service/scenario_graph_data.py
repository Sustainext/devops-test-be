from collections import defaultdict
import copy
from apps.optimize.models.SelectedActivityModel import SelectedActivity
from apps.optimize.models.CalculatedResult import CalculatedResult
from apps.optimize.models.BusinessMetric import BusinessMetric
from apps.optimize.filters import CalculatedResultFilter
from django.shortcuts import get_object_or_404
from common.utils.value_types import format_decimal_places


class ScenarioGraphService:
    def __init__(self, scenario, filters=None):
        self.scenario = scenario
        self.filters = filters
        self.selected_activities = SelectedActivity.objects.filter(scenario=scenario)
        self.business_metric = get_object_or_404(BusinessMetric, scenario=scenario)

    def get_filtered_results(self):
        queryset = CalculatedResult.objects.filter(scenario=self.scenario)
        return CalculatedResultFilter(self.filters, queryset=queryset).qs.order_by(
            "year", "metric"
        )

    def get_year_map_data(self, results):
        year_map = defaultdict(list)
        activity_map = {str(act.uuid): act for act in self.selected_activities}

        for res in results:
            year = str(res.year)
            metric = res.metric
            weightage_key = f"{metric}_weightage"
            weightage = getattr(self.business_metric, weightage_key, 0)
            co2e = round(res.result.get("co2e", 0) / 1000, 4)
            value = co2e * weightage  # Tonnes

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
            value = round(value, 3)
            if existing:
                existing[metric] = value
                existing["decarbonization"] = (
                    existing["decarbonization"] or decarbonization
                )
                existing["co2e"] += co2e
            else:
                year_map[year].append(
                    {
                        "uuid": uuid_str,
                        "scope": res.scope,
                        "category": res.category,
                        "sub_category": res.sub_category,
                        "activity_name": res.activity_name,
                        "activity_id": res.activity_id,
                        "co2e": co2e,
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
                for metric in metrics:
                    if metric in entry:
                        totals[year][metric] += entry[metric]

        final_totals = {}
        for year, metric_totals in totals.items():
            year_total = sum(metric_totals.values())
            metric_totals["total"] = year_total
            final_totals[year] = dict(metric_totals)

        return final_totals

    def get_base_year_unselected_data(self, year_map):
        selected_keys = {str(sa.uuid) for sa in self.selected_activities}
        base_year_data = copy.deepcopy(year_map.get(str(self.scenario.base_year), []))
        filtered = [
            entry for entry in base_year_data if entry["uuid"] not in selected_keys
        ]
        return {str(self.scenario.base_year): filtered}

    def round_of_totals_response(self, totals):
        for year, metrics_dict in totals.items():
            for metric, value in metrics_dict.items():
                metrics_dict[metric] = format_decimal_places(value)
        return totals

    def single_scenario_response(self, results):
        year_map = self.get_year_map_data(results)
        totals = self.add_total_dict(year_map, results)
        base_year_unselected_data = self.get_base_year_unselected_data(year_map)
        excluded_totals = self.add_total_dict(base_year_unselected_data, results)

        base_year_str = str(self.scenario.base_year)
        excluded_values = excluded_totals.get(base_year_str, {})

        for year, metrics_dict in totals.items():
            if year == base_year_str:
                continue
            for metric, value in excluded_values.items():
                metrics_dict[metric] += value

        totals = self.round_of_totals_response(totals)

        return {
            "metadata": {
                "unit": "t",
                "baseYear": self.scenario.base_year,
                "targetYear": self.scenario.target_year,
                "years": [
                    str(y)
                    for y in range(
                        self.scenario.base_year, self.scenario.target_year + 1
                    )
                ],
            },
            "totals": totals,
            "yearly_data": year_map,
        }

    def build_response(self):
        results = self.get_filtered_results()
        year_map = self.get_year_map_data(results)
        totals = self.add_total_dict(year_map, results)

        base_year_data = self.get_base_year_unselected_data(year_map)
        excluded_totals = self.add_total_dict(base_year_data, results)
        base_year_str = str(self.scenario.base_year)
        excluded_values = excluded_totals.get(base_year_str, {})

        for year, metric_dict in totals.items():
            if year == base_year_str:
                continue
            for metric, value in excluded_values.items():
                metric_dict[metric] += value

        totals = self.round_of_totals_response(totals)

        return {
            "metadata": {
                "unit": "t",
                "baseYear": self.scenario.base_year,
                "targetYear": self.scenario.target_year,
                "years": [
                    str(y)
                    for y in range(
                        self.scenario.base_year, self.scenario.target_year + 1
                    )
                ],
            },
            "totals": totals,
            "yearly_data": year_map,
        }
