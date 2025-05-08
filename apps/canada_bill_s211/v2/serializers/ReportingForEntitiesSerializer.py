from rest_framework import serializers
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities

class ReportingForEntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingForEntities
        fields = '__all__'
