from collections import defaultdict
from operator import itemgetter
from datametric.utils.analyse import filter_by_start_end_dates
from common.utils.value_types import format_decimal_places, safe_percentage
from datametric.models import DataPoint


def calculate_scope_contribution(key_name, scope_total_values):
    total_emissions = sum(scope_total_values.values())
    scope_contributions = []
    for scope_name, scope_value in scope_total_values.items():
        try:
            contribution = safe_percentage(scope_value, total_emissions)
        except ZeroDivisionError:
            contribution = 0
        scope_contributions.append(
            {
                key_name: scope_name,
                "total": format_decimal_places(scope_value / 1000),
                "contribution": contribution,
                "Units": "tC02e",
            }
        )
    scope_contributions.sort(key=itemgetter("contribution"), reverse=True)
    return scope_contributions


def get_top_emission_by_scope(locations, user, start, end, path_slug):
    # * Get all Raw Responses based on location and year.
    data_points = (
        DataPoint.objects.filter(
            json_holder__isnull=False,
            is_calculated=True,
            path__slug__icontains="gri-collect-emissions-scope-combined",
            locale__in=locations,
            client_id=user.client.id,
        )
        .select_related("raw_response")
        .filter(filter_by_start_end_dates(start_date=start, end_date=end))
    )

    top_emission_by_scope = defaultdict(lambda: 0)
    top_emission_by_source = defaultdict(lambda: 0)
    top_emission_by_location = defaultdict(lambda: 0)

    for data_point in data_points:
        top_emission_by_scope[path_slug[data_point.raw_response.path.slug]] += sum(
            [i.get("co2e", 0) for i in data_point.json_holder]
        )
        top_emission_by_location[data_point.locale.name] += sum(
            [i.get("co2e", 0) for i in data_point.json_holder]
        )
        for emission_request, climatiq_response in zip(
            data_point.raw_response.data, data_point.json_holder
        ):
            top_emission_by_source[emission_request["Emission"]["Category"]] += (
                climatiq_response.get("co2e", 0)
            )

    return top_emission_by_scope, top_emission_by_source, top_emission_by_location
