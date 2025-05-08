from rest_framework import serializers
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from sustainapp.models import Corporateentity


class ReportingForEntitiesSerializer(serializers.ModelSerializer):
    corporate = serializers.PrimaryKeyRelatedField(
        queryset=Corporateentity.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ReportingForEntities
        fields = '__all__'
