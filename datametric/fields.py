import demjson3
from rest_framework import serializers


class JavaScriptObjectField(serializers.JSONField):
    """
    A custom serializer field that accepts a JavaScript object literal string
    and decodes it into a valid Python dictionary.
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                return demjson3.decode(data)
            except demjson3.JSONDecodeError as e:
                raise serializers.ValidationError(
                    f"Invalid JavaScript object format: {e}"
                )
        return super().to_internal_value(data)
