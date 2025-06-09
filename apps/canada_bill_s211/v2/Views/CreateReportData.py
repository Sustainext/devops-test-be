from apps.canada_bill_s211.v2.services.bill_s211_data import BillS211ScreenDataService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.canada_bill_s211.v2.serializers.CheckBillS211ReportSerializer import CreateBillS211ReportSerializer
from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report

class CreateOrEditReportData(APIView):
    """
    API view to create or edit (upsert) Bill S211 report data for a specific screen.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = CreateBillS211ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.validated_data["report"]
        screen = serializer.validated_data["screen"]
        try:
            bill_s211_report = BillS211Report.objects.get(report=report, screen=screen)
            updating_serializer = CreateBillS211ReportSerializer(instance=bill_s211_report, data=request.data)
            updating_serializer.is_valid(raise_exception=True)
            updating_serializer.save()
            return Response(data=updating_serializer.data, status=status.HTTP_200_OK)
        except BillS211Report.DoesNotExist:
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
