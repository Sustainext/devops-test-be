from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report
from rest_framework import serializers

class GetBillS211ReportSerializer(serializers.Serializer):
    bill_s211_report = serializers.PrimaryKeyRelatedField(
        queryset=BillS211Report.objects.all(),
        required=True
    )

class CreateBillS211ReportSerializer(serializers.Serializer):
    bill_s211_report = serializers.PrimaryKeyRelatedField(
        queryset=BillS211Report.objects.all(),
        required=True
    )

    class Meta:
        model = BillS211Report
        fields = "__all__"
