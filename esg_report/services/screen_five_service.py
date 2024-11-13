from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from esg_report.models import AwardAndRecognition
from esg_report.Serializer.AwardsAndRecognitionSerializer import (
    AwardsAndRecognitionSerializer,
)
from sustainapp.models import Report


class AwardsAndRecognitionService:
    @staticmethod
    def get_awards_and_recognition_by_report_id(report_id):
        """
        Fetch the AwardAndRecognition associated with a Report.
        """
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return {"error": "Report not found", "status": status.HTTP_404_NOT_FOUND}

        try:
            award_recognition = report.award_recognition
            return AwardsAndRecognitionSerializer(award_recognition).data
        except (AwardAndRecognition.DoesNotExist, ObjectDoesNotExist):
            return None
