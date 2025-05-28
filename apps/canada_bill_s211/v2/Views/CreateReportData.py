from apps.canada_bill_s211.v2.services.bill_s211_data import BillS211ScreenDataService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.canada_bill_s211.v2.serializers.CheckBillS211ReportSerializer import CreateBillS211ReportSerializer

class CreateReportData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateBillS211ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
