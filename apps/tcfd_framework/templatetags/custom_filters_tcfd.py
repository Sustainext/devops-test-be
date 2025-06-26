import re
from django import template

register = template.Library()


@register.filter
def remove_extra_br(value):
    """
    Replace multiple consecutive <br>, <br/>, or <br /> tags with a single <br />
    (case-insensitive).
    """
    # Pattern matches one or more sequential <br>, <br/>, or <br /> (case-insensitive, optional whitespace)
    return re.sub(r"(?:<br\s*/?>\s*){2,}", "<br />", value, flags=re.IGNORECASE)


@register.filter
def remove_br_after_p(value):
    """
    Remove <br>, <br/>, <br /> tags that immediately follow </p>
    """
    return re.sub(r"</p>\s*<br\s*/?>", "</p>", value, flags=re.IGNORECASE)
