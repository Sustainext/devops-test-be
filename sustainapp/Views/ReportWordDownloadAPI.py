from rest_framework.views import APIView
from sustainapp.utils import word_docx_report
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Report, AnalysisData2
import logging

logger = logging.getLogger("custom_logger")


class ReportWordDownloadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            Report.objects.only("pk").get(pk=pk)
            AnalysisData2.objects.only("report_id").get(report_id=pk)
        except (Report.DoesNotExist, AnalysisData2.DoesNotExist):
            raise ValidationError(f"Report with id {pk} does not exist")
        try:
            response = word_docx_report(pk=pk)
        except Exception as e:
            logger.info("Error generating word report", exc_info=True)
            logger.error(e)
            raise APIException("Error generating word report")
        return response
