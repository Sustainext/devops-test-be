from decimal import Decimal


def get_integer(value):
    try:
        return int(value)
    except ValueError:
        return 0


def get_decimal(value):
    try:
        return round(Decimal(value), 4)
    except (ValueError, TypeError):
        return 0


def get_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
