from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from esg_report.models import MissionVisionValues
from esg_report.Serializer.MissionVisionValuesSerializer import (
    MissionVisionValuesSerializer,
)
from sustainapp.models import Report


class MissionVisionValuesService:
    @staticmethod
    def get_mission_vision_values_by_report_id(report_id):
        """
        Fetch the MissionVisionValues associated with a Report.
        """
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return {"error": "Report not found", "status": status.HTTP_404_NOT_FOUND}

        try:
            mission_vision_values = report.mission_vision_values
            return MissionVisionValuesSerializer(mission_vision_values).data
        except (MissionVisionValues.DoesNotExist, ObjectDoesNotExist):
            return {
                "error": "Mission Vision Values not found",
                "status": status.HTTP_404_NOT_FOUND,
            }
