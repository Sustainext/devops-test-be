from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")


@register.filter
def sum_values(data, key):
    total = 0.0  # Initialize as a float
    if isinstance(data, dict):
        # Handle case where data is a dictionary of lists
        for item_list in data.values():
            if isinstance(item_list, list):
                total += sum(
                    float(item.get(key, 0))
                    for item in item_list
                    if isinstance(item, dict) and key in item
                )
    elif isinstance(data, list):
        # Handle case where data is a list of dictionaries
        total = sum(
            float(item.get(key, 0))
            for item in data
            if isinstance(item, dict) and key in item
        )
    # Round the total to 5 decimal places
    return round(total, 5)


@register.filter
def round_to(value, decimal_places):
    try:
        return round(float(value), int(decimal_places))
    except (ValueError, TypeError):
        return value


@register.filter
def dict_get(dictionary, key):
    """Safely get a value from a dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "No data available")
    return "No data available"


@register.filter
def nested_dict_get(dictionary, keys):
    """Safely get a nested value from a dictionary using a series of keys."""
    try:
        for key in keys.split("."):
            dictionary = dictionary.get(key, {})
            print(dictionary)
        return dictionary or "No data available"
    except AttributeError:
        return "No data available"


@register.filter
def get_wage(wages, location):
    # Replace any hyphens with underscores to match the data structure
    location_key = location.replace("-", "_")
    return wages.get(location_key, {})
