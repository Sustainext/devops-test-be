from rest_framework import serializers


# Nested serializer for the 'omission' field
class OmissionSerializer(serializers.Serializer):
    req_omitted = serializers.CharField(allow_null=True)
    reason = serializers.CharField(required=False,allow_null=True)
    explanation = serializers.CharField(required=False, allow_null=True)


# Main serializer for each dictionary in the list
class DataItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    page_number = serializers.IntegerField(allow_null=True)
    gri_sector_no = serializers.IntegerField(allow_null=True)
    is_filled = serializers.BooleanField()
    omission = OmissionSerializer(many=True)


# Serializer for the list itself
class DataListSerializer(serializers.Serializer):
    items = serializers.ListSerializer(child=DataItemSerializer())
