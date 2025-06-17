from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ESGCustomReport import EsgCustomReport
from esg_report.Serializer.CustomEsgReportSerializer import CustomEsgReportSerializer


class CustomEsgReportView(APIView):
    """
    View for handling custom ESG report requests.
    Request:
        - GET: Retrieve custom ESG report data based on the report ID.
        - Patch: Update an existing custom ESG report.
    """

    def skip_first_page(self, data):
        skip_first_page = False
        for page_data in data:
            if page_data["enabled"]:
                skip_first_page = True
                break
        return skip_first_page

    def get(self, request, report_id):
        try:
            custom_report = EsgCustomReport.objects.get(report_id=report_id)
            skip_first_page = self.skip_first_page(custom_report.section)
            serializer = CustomEsgReportSerializer(custom_report)
            data = serializer.data
            data["skip_first_page"] = skip_first_page

            return Response(
                {"data": data},
                status=status.HTTP_200_OK,
            )
        except EsgCustomReport.DoesNotExist:
            return Response(
                {"error": "Custom report not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, report_id):
        try:
            custom_report = EsgCustomReport.objects.get(report_id=report_id)
            serializer = CustomEsgReportSerializer(
                custom_report, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Data updated successfully."}, status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EsgCustomReport.DoesNotExist:
            return Response(
                {"error": "Custom report not found"}, status=status.HTTP_404_NOT_FOUND
            )
