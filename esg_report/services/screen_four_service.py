from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from esg_report.models import SustainabilityRoadmap
from esg_report.Serializer.SustainabilityRoadmapSerializer import (
    SustainabilityRoadmapSerializer,
)
from sustainapp.models import Report


class SustainabilityRoadmapService:
    @staticmethod
    def get_sustainability_roadmap_by_report_id(report_id):
        """
        Fetch the SustainabilityRoadmap associated with a Report.
        """
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return {"error": "Report not found", "status": status.HTTP_404_NOT_FOUND}

        try:
            sustainability_roadmap = report.sustainability_roadmap
            return SustainabilityRoadmapSerializer(sustainability_roadmap).data
        except (SustainabilityRoadmap.DoesNotExist, ObjectDoesNotExist):
            return None
