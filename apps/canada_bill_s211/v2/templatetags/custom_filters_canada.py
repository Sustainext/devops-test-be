import re
from django import template

register = template.Library()


@register.filter
def remove_br(value):
    """Remove all <br>, <br/>, and <br /> tags (case-insensitive)"""
    return re.sub(r"<br\s*/?>", "", value, flags=re.IGNORECASE)
