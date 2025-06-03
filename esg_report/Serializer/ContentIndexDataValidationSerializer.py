from rest_framework import serializers


class OmissionSerializer(serializers.Serializer):
    req_omitted = serializers.CharField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_null=True)
    explanation = serializers.CharField(required=False, allow_null=True)

class ContentIndexItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField(required=False, allow_null=True)
    page_number = serializers.IntegerField(required=False, allow_null=True)
    gri_sector_no = serializers.CharField(required=False, allow_null=True)
    is_filled = serializers.BooleanField()
    omission = serializers.ListField(child=OmissionSerializer(), required=False, allow_empty=True)

class Heading3SectionSerializer(serializers.Serializer):
    heading3 = serializers.CharField()
    items = serializers.ListField(child=ContentIndexItemSerializer())

class Heading2SectionSerializer(serializers.Serializer):
    heading2 = serializers.CharField()
    sections = serializers.ListField(child=Heading3SectionSerializer())

class DisclosureSectionSerializer(serializers.Serializer):
    heading1 = serializers.CharField()
    items = serializers.ListField(child=ContentIndexItemSerializer(), required=False)
    sections = serializers.ListField(child=Heading2SectionSerializer(), required=False)

class ContentIndexUpdateSerializer(serializers.Serializer):
    sections = serializers.ListField(child=DisclosureSectionSerializer())
