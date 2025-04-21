from collections import defaultdict
from operator import itemgetter
from datametric.utils.analyse import filter_by_start_end_dates
from common.utils.value_types import format_decimal_places, safe_percentage
from datametric.models import DataPoint
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from common.utils.value_types import safe_divide


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
                "Units": "tCO2e",
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
        .filter(filter_by_start_end_dates(start_date=start, end_date=end))
    )

    top_emission_by_scope = defaultdict(lambda: 0)
    top_emission_by_source = defaultdict(lambda: 0)
    top_emission_by_location = defaultdict(lambda: 0)
    gases_data = []

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
            gases_data.append(climatiq_response.get("constituent_gases", {}))

    return (
        top_emission_by_scope,
        top_emission_by_source,
        top_emission_by_location,
        gases_data,
    )


def disclosure_analyze_305_5(data_points):
    data = collect_data_by_raw_response_and_index(data_points)
    form_data = [entry for item in data for entry in item["formData"]]
    results = []
    for data in form_data:
        initiative_taken = data.get("Q2", None)
        method = data.get("Q3", None)
        others_method = data.get("customUnit", None)
        base_year_or_base_inline = data.get("Q4", None)
        year_dict = data.get("Q5", None)
        rationale = data.get("Q6", None)
        ghg_emission_reduced = data.get("Q7", None)
        scopes = data.get("Q8", None)
        gases_included = data.get("Q9", None)
        assumption_or_calculation = data.get("Q10", None)

        if method == "Other (please specify)":
            method = others_method

        year = f"{year_dict['start']} - {year_dict['end']}" if year_dict else None
        results.append(
            {
                "initiative_taken": initiative_taken,
                "method": method,
                "base_year_or_base_inline": base_year_or_base_inline,
                "year": year,
                "rationale": rationale,
                "ghg_emission_reduced": ghg_emission_reduced,
                "scopes": scopes,
                "gases_included": gases_included,
                "assumption_or_calculation": assumption_or_calculation,
            }
        )
    return results


def validate_gases_constituent(gases_data):
    ch4 = n2o = co2 = False

    for data in gases_data:
        if not isinstance(data, dict):
            continue

        if not ch4 and data.get("ch4", None) is not None and data.get("ch4", 0) > 0:
            ch4 = True
        if not n2o and data.get("n2o", None) is not None and data.get("n2o", 0) > 0:
            n2o = True
        if not co2 and data.get("co2", None) is not None and data.get("co2", 0) > 0:
            co2 = True

        # If all gases are found, break early
        if ch4 and n2o and co2:
            break

    return ch4, n2o, co2


def ghg_emission_intensity(data, top_emission, gases_data):
    raw_data = collect_data_by_raw_response_and_index(data)
    if not top_emission:
        return []

    results = []
    emission = top_emission
    total_emission = sum(emission.values()) / 1000
    ch4, n2o, co2 = validate_gases_constituent(gases_data)
    for data in raw_data:
        organization_metric = data.get("MetricType", None)
        other_metric = data.get("customMetricType", None)
        quantity = data.get("Quantity", None)
        unit = data.get("Units", None)
        other_metric_unit = data.get("customUnit", None)
        type_of_ghg = data.get("intensityratio", None)
        organization_metric = data.get("MetricType", None)

        ghg_emission_intensity = safe_divide(total_emission, quantity)

        if organization_metric == "Other (please specify)":
            organization_metric = other_metric
            unit = other_metric_unit
        ghg_intensity_unit = f"tCO2e/{unit}"
        results.append(
            {
                "organization_metric": organization_metric,
                "quantity": quantity,
                "unit": unit,
                "type_of_ghg": type_of_ghg,
                "ghg_emission_intensity": ghg_emission_intensity,
                "ghg_intensity_unit": ghg_intensity_unit,
                "ch4": ch4,
                "n2o": n2o,
                "co2": co2,
                "HFCs": False,
                "PFCs": False,
                "SF6": False,
                "NF3": False,
            }
        )
    return results
