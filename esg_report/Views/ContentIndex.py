from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import MaterialityAssessment, MaterialTopic, Disclosure
from datametric.models import Path
from sustainapp.models import Report
from esg_report.utils import get_materiality_assessment


class GetContentIndex(APIView):
    permission_classes = [IsAuthenticated]

    def get_general_topics_and_disclosures(self):
        general_disclosures = Disclosure.objects.filter(topic__esg_category="general")
        return 

    def get(self, request, report_id: int, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # * Get general material topics and disclosures
        self.materiality_assessment = get_materiality_assessment(self.report)
