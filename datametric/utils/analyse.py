from sustainapp.models import Location, Corporateentity, Organization
from django.db.models import Prefetch
from rest_framework import serializers
from datetime import date, timedelta
from django.db.models import Q


def set_locations_data(organisation, corporate, location):
    """
    If Organisation is given and Corporate and Location is not given, then get all corporate locations
    If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
    If Location is given, then get only that location
    """
    if organisation and corporate and location:
        locations = Location.objects.filter(id=location.id)
    elif location is None and corporate and organisation:
        locations = corporate.location.all()
    elif location is None and corporate is None and organisation:
        locations = Location.objects.prefetch_related(
            Prefetch(
                "corporateentity",
                queryset=organisation.corporatenetityorg.all(),
            )
        ).filter(corporateentity__in=organisation.corporatenetityorg.all())
    else:
        raise serializers.ValidationError(
            "Not send any of the following fields: organisation, corporate, location"
        )

    return locations


def get_year_month_combinations(start_date, end_date):
    current_date = start_date
    year_month_combinations = []

    while current_date <= end_date:
        year_month_combinations.append((current_date.year, current_date.month))
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)

    return year_month_combinations


def filter_by_start_end_dates(start_date, end_date):
    year_month_combinations = get_year_month_combinations(start_date, end_date)
    q_objects = Q()

    for year, month in year_month_combinations:
        q_objects |= Q(year=year, month=month)

    return q_objects


def safe_divide(numerator, denominator, decimal_places=2):
    return (
        round((numerator / denominator * 100), decimal_places)
        if denominator != 0
        else 0
    )


def get_raw_response_filters(organisation=None, corporate=None, location=None):
    locations = set_locations_data(organisation, corporate, location)

    filters = Q()
    if organisation:
        filters |= Q(organization=organisation)
    if corporate:
        filters |= Q(corporate=corporate)
    if locations.exists():
        filters |= Q(locale__in=locations)

    return filters
