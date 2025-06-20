from sustainapp.models import Report
from datametric.models import RawResponse, DataPoint, EmissionAnalysis
from django.db.models import Q
import logging
from datametric.utils.analyse import set_locations_data
from sustainapp.Utilities.emission_analyse import (
    get_top_emission_by_scope,
    calculate_scope_contribution,
    disclosure_analyze_305_5,
    ghg_emission_intensity,
)

logger = logging.getLogger("file")


def get_maximum_months_year(report: Report):
    """
    Get the maximum months year from the given report's start and end dates.
    This function determines the year that has the maximum number of months between the report's start and end dates. If both dates are in the same year, it returns that year. Otherwise, it calculates the number of months in the start and end years and returns the year with the maximum number of months.

    Args:
        report (Report): The report object containing the start and end dates.

    Returns:
        int: The year with the maximum number of months between the report's start and end dates.
    """
    # Extracting start_date and end_date
    start_date = report.start_date
    end_date = report.end_date

    # Getting the years for start_date and end_date
    start_year = start_date.year
    end_year = end_date.year

    # If both dates are in the same year
    if start_year == end_year:
        return start_year

    # Months in the start year
    months_start_year = 12 - start_date.month + 1

    # Months in the end year
    months_end_year = end_date.month

    # Determine which year has the maximum months
    if months_start_year > months_end_year:
        return start_year
    elif months_start_year == months_end_year:
        return end_date.year
    else:
        return end_year


def get_data_points_as_per_report(report: Report):
    """
    Get DataPoints as per report.
    """
    data_points = DataPoint.objects.filter(client_id=report.client.id)
    if report.corporate:
        data_points = data_points.filter(
            Q(corporate=report.corporate)
            | Q(organization=report.organization)
            | Q(locale__in=report.corporate.location.all())
            | Q(locale=None)
        )
    elif report.organization:
        data_points = data_points.filter(
            Q(organization=report.organization)
            | Q(
                locale__in=report.organization.corporatenetityorg.all().values_list(
                    "location", flat=True
                )
            )
        )

    return data_points.filter(year=get_maximum_months_year(report))


def get_raw_responses_as_per_report(report: Report):
    """
    Get RawResponses as per report.

    Situation in RawResponses.
    1. If corporate is given, then organization would also be given.
    2. If corporate is not given, then organization will be given.
    3. If corporate and organization are not given, then locale will be given.
    Now Create a filter for each of this.
    and then combine them.
    """
    raw_responses = RawResponse.objects.filter(client=report.client)
    if report.corporate:
        raw_responses = raw_responses.filter(
            Q(corporate=report.corporate) | Q(organization=report.organization)
        )
        raw_responses = raw_responses.filter(
            Q(locale__in=report.corporate.location.all()) | Q(locale=None)
        )
    elif report.organization:
        raw_responses = raw_responses.filter(
            Q(organization=report.organization)
            | Q(
                locale__in=report.organization.corporatenetityorg.all().values_list(
                    "location", flat=True
                )
            )
        )
    return raw_responses.filter(year=get_maximum_months_year(report))


def get_emission_analysis_as_per_report(report: Report):
    """
    Get EmissionAnalysis Objects as per report.
    """
    emission_analysis_objects = EmissionAnalysis.objects.filter(
        raw_response__in=get_raw_responses_as_per_report(report)
    )

    return emission_analysis_objects


def get_emission_analyse_as_per_report(report: Report, data_points):
    """
    Common method across the project that gives you emission analyse data.
    """
    locations = set_locations_data(
        organisation=report.organization,
        corporate=report.corporate,
        location=None,
    )
    (
        top_emission_by_scope,
        top_emission_by_source,
        top_emission_by_location,
        gases_data,
    ) = get_top_emission_by_scope(
        locations=locations,
        user=report.user,
        start=report.start_date,
        end=report.end_date,
        path_slug={
            "gri-environment-emissions-301-a-scope-1": "Scope 1",
            "gri-environment-emissions-301-a-scope-2": "Scope 2",
            "gri-environment-emissions-301-a-scope-3": "Scope 3",
        },
    )

    # * Prepare response data
    response_data = dict()
    response_data["all_emission_by_scope"] = calculate_scope_contribution(
        key_name="scope", scope_total_values=top_emission_by_scope
    )
    response_data["all_emission_by_source"] = calculate_scope_contribution(
        key_name="source", scope_total_values=top_emission_by_source
    )
    response_data["all_emission_by_location"] = calculate_scope_contribution(
        key_name="location", scope_total_values=top_emission_by_location
    )
    response_data["top_5_emisson_by_source"] = response_data["all_emission_by_source"][
        0:5
    ]
    response_data["top_5_emisson_by_location"] = response_data[
        "all_emission_by_location"
    ][0:5]
    response_data["disclosure_analyze_305_5"] = disclosure_analyze_305_5(
        data_points.filter(
            path__slug="gri-environment-emissions-GHG-emission-reduction-initiatives"
        )
    )
    response_data["ghg_emission_intensity"] = ghg_emission_intensity(
        data_points.filter(
            path__slug="gri-environment-emissions-GHG emission-intensity"
        ),
        top_emission_by_scope,
        gases_data,
    )
    return response_data
