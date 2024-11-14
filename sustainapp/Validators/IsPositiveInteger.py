from django.core.exceptions import ValidationError


def validate_positive_integer(value):
    try:
        value = int(value)
        if value < 0:
            raise ValidationError("Value must be a positive integer.")
    except (TypeError, ValueError):
        raise ValidationError("Value must be a positive integer.")
