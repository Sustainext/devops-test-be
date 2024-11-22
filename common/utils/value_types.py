from decimal import Decimal
import logging

logger = logging.getLogger("error.log")


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


def format_decimal_places(value):
    """
    Format decimal places based on value:
    - For values < 1: returns up to 4 decimal places
    - For values >= 1: returns up to 2 decimal places
    """
    try:
        decimal_value = Decimal(str(value))
        if abs(decimal_value) < 1:
            return float(round(decimal_value, 4))
        return float(round(decimal_value, 2))
    except (ValueError, TypeError):
        logger.info(f"Error formatting decimal places: {value}", exc_info=True)
        return float(Decimal("0"))


def safe_divide(numerator, denominator):
    return format_decimal_places(((numerator / denominator)) if denominator != 0 else 0)
