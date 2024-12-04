from sustainapp.models import Location, Corporateentity, Organization
from django.db.models import Prefetch
from rest_framework import serializers
from datetime import date, timedelta
from django.db.models import Q
from common.utils.value_types import safe_divide


def set_locations_data(organisation, corporate, location):
    """
    If Organisation is given and Corporate and Location is not given, then get all corporate locations
    If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
    If Location is given, then get only that location
    """
    if location and corporate and organisation:  # * If all three are given
        locations = Location.objects.filter(id=location.id)
    elif (
        location is None and corporate and organisation
    ):  # * If location is not given, corporate and organisation are given
        locations = corporate.location.all()
    elif (
        location is None and corporate is None and organisation
    ):  # * If location and corporate is not given and organisation are given
        locations = Location.objects.filter(
            corporateentity__in=organisation.corporatenetityorg.all()
        )
    elif (
        location and corporate is None and organisation is None
    ):  # * If location is given and corporate and organisation are not given
        locations = Location.objects.filter(id=location.id)
    elif (
        location is None and corporate is None and organisation is None
    ):  # * If all three are not given
        locations = Location.objects.none()
    elif (
        location is None and corporate and organisation is None
    ):  # * If location is not given, corporate is given and organisation is not given
        locations = corporate.location.all()
    else:
        locations = Location.objects.none()

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
        q_objects |= Q(year=year, month=month) | Q(year=year, month=None)

    return q_objects


def safe_divide_percentage(numerator, denominator):
    return safe_divide(numerator, denominator) * 100


def safe_integer_divide(numerator, denominator, decimal_places=2):
    try:
        return safe_divide(int(numerator), int(denominator)) * 100
    except (ZeroDivisionError, ValueError):
        return 0


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


def get_sum_from_dictionary_list(dictionary_list, key):
    """
    This function takes a list of dictionaries and a key as input and returns the sum of the values associated with the key in all dictionaries in the list.
    """
    return sum(dictionary.get(key, 0) for dictionary in dictionary_list)


def convert_from_str_into_int(string):
    """
    This function takes a string as input and returns an integer if the string is a valid integer, otherwise it returns the original string.
    """
    try:
        return int(string)
    except ValueError:
        return 0
