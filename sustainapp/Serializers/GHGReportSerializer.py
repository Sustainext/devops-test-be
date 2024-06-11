from sustainapp.models import AnalysisData2
from rest_framework import serializers
from rest_framework import serializers
from sustainapp.models import Organization, Corporateentity
from datametric.models import RawResponse


class ActivityDataSerializer(serializers.Serializer):
    activity_unit = serializers.CharField()
    activity_value = serializers.FloatField()


class EmissionSerializer(serializers.Serializer):
    category = serializers.CharField()
    subcategory = serializers.CharField()
    activity = serializers.CharField()
    quantity = serializers.CharField()
    unit = serializers.CharField()


class ScopeDataSerializer(serializers.Serializer):
    scope_name = serializers.CharField()
    total_co2e = serializers.FloatField()
    contribution_scope = serializers.FloatField()
    co2e_unit = serializers.CharField()
    unit_type = serializers.CharField()
    unit1 = serializers.CharField()
    unit2 = serializers.CharField(allow_blank=True, required=False)
    activity_data = ActivityDataSerializer()


class LocationDataSerializer(serializers.Serializer):
    location_name = serializers.CharField()
    location_address = serializers.CharField()
    location_type = serializers.CharField()
    total_co2e = serializers.FloatField()
    contribution_scope = serializers.FloatField()


class ScouceDataSerializer(serializers.Serializer):
    scope_name = serializers.CharField()
    source_name = serializers.CharField()
    category_name = serializers.CharField()
    activity_name = serializers.CharField()
    total_co2e = serializers.FloatField()
    co2e_unit = serializers.CharField()
    unit_type = serializers.CharField()
    unit1 = serializers.CharField()
    unit2 = serializers.CharField(allow_blank=True, required=False)
    source = serializers.CharField()
    activity_data = ActivityDataSerializer()
    contribution_source = serializers.FloatField()


class GHGReportRawResponseSerializer(serializers.Serializer):
    corporate_name = serializers.CharField()
    scopes = ScopeDataSerializer(many=True)
    locations = LocationDataSerializer(many=True)
    sources = ScouceDataSerializer(many=True)


class AnalysisData2Serializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisData2
        fields = "__all__"


class CheckReportDataSerializer(serializers.Serializer):
    start_month = serializers.IntegerField(min_value=1, max_value=12, required=True)
    end_month = serializers.IntegerField(min_value=1, max_value=12, required=True)
    year = serializers.IntegerField(required=True)

    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(), required=False
    )
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), required=False
    )

    class Meta:
        fields = ("start_month", "end_month", "year", "corporate", "organisation")
