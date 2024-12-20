from datametric.models import DataPoint
from collections import defaultdict
from common.utils.value_types import safe_percentage


def get_data(year, client_id, filter_by):
    dp_data = DataPoint.objects.filter(
        path__slug="gri-social-supplier_screened-414-1a-number_of_new_suppliers",
        client_id=client_id,
        year=year,
        **filter_by,
    )
    pos_data = DataPoint.objects.filter(
        path__slug="gri-social-impacts_and_actions-414-2a-2d-2e-negative_social_impacts",
        client_id=client_id,
        year=year,
        **filter_by,
    )
    return dp_data, pos_data


def get_social_data(data_points):
    new_supplier_data = defaultdict(lambda: 0.0)
    metric_mapping = {
        "Q1": "total_new_suppliers",
        "Q2": "total_suppliers",
    }

    for data in data_points:
        metric_key = metric_mapping.get(data.metric_name)
        if metric_key:
            new_supplier_data[metric_key] += float(data.value)

    total_new_suppliers = new_supplier_data["total_new_suppliers"]
    total_suppliers = new_supplier_data["total_suppliers"]
    new_supplier_data["percentage"] = safe_percentage(
        total_new_suppliers, total_suppliers
    )

    return new_supplier_data


def get_pos_data(data_points):
    pos = defaultdict(lambda: 0.0)
    metric_mapping = {
        "Q1": "total_number_of_negative_suppliers",
        "Q2": "total_number_of_improved_suppliers",
        "Q3": "total_number_of_suppliers_assessed",
    }

    for data in data_points:
        metric_key = metric_mapping.get(data.metric_name)
        if metric_key:
            pos[metric_key] += float(data.number_holder)

    total_number_of_negative_suppliers = pos["total_number_of_negative_suppliers"]
    total_number_of_improved_suppliers = pos["total_number_of_improved_suppliers"]
    total_number_of_suppliers_assessed = pos["total_number_of_suppliers_assessed"]

    pos["percentage_negative"] = safe_percentage(
        total_number_of_negative_suppliers, total_number_of_suppliers_assessed
    )
    pos["percentage_improved"] = safe_percentage(
        total_number_of_improved_suppliers, total_number_of_suppliers_assessed
    )

    return pos


def filter_non_zero_values(data):
    return {k: v for k, v in data.items() if v != 0.0}
