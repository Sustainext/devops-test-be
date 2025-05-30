from sustainapp.models import Report
from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report
from rest_framework import serializers

class GetBillS211ReportSerializer(serializers.Serializer):
    report = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(),
        required=True
    )
    screen = serializers.IntegerField()

class CreateBillS211ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillS211Report
        fields = "__all__"
