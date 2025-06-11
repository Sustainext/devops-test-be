from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ESGCustomReport import EsgCustomReport
from esg_report.Serializer.CustomEsgReportSerializer import CustomEsgReportSerializer


class CustomEsgReportView(APIView):
    def get(self, request, report_id):
        try:
            custom_report = EsgCustomReport.objects.get(report_id=report_id)
            serializer = CustomEsgReportSerializer(custom_report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EsgCustomReport.DoesNotExist:
            return Response(
                {"error": "Custom report not found"}, status=status.HTTP_404_NOT_FOUND
            )
