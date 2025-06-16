"""
Splits a string value by the provided key and returns the resulting list.

Args:
    value (str): The string to be split.
    key (str): The character or substring to split the string on.

Returns:
    list: A list of substrings from the original string, split by the provided key.
"""

from django import template
from common.utils.value_types import format_decimal_places
register = template.Library()


@register.filter
def split_string(value, key):
    if value is None:
        return ""
    return value.split(key)

@register.filter
def get_scope_total(scopes, name):
    for scope in scopes:
        if scope.get("scope_name") == name:
            return float(format_decimal_places(scope.get("total_co2e", 0.0)))
    return 0.0
