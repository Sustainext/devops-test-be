from apps.canada_bill_s211.v2.services.bill_s211_data import BillS211ScreenDataService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.canada_bill_s211.v2.serializers.CheckBillS211ReportSerializer import GetBillS211ReportSerializer

class GetReportData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetBillS211ReportSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        service = BillS211ScreenDataService(report=serializer.validated_data["bill_s211_report"])
        data = service.get_introduction_page_data()
        return Response(data, status=status.HTTP_200_OK)
