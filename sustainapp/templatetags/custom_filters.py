"""
Splits a string value by the provided key and returns the resulting list.

Args:
    value (str): The string to be split.
    key (str): The character or substring to split the string on.

Returns:
    list: A list of substrings from the original string, split by the provided key.
"""

from django import template

register = template.Library()


@register.filter
def split_string(value, key):
    if value is None:
        return ""
    return value.split(key)
