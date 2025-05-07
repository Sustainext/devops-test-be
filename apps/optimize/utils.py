# utils/fields.py
from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP


class RoundedDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        if value is None:
            return None
        return float(Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
