from esg_report.models.ScreenOne import CeoMessage
from sustainapp.models import Report


class CeoMessageService:
    """
    Service class to handle business logic for CEO messages.
    """

    @staticmethod
    def get_report_by_id(esg_report_id):
        """
        Fetch a Report object by its ID.
        """
        return Report.objects.get(id=esg_report_id)

    @staticmethod
    def get_ceo_message_by_report(report):
        """
        Fetch the CEO message for a given report.
        """
        try:
            return CeoMessage.objects.get(report=report)
        except CeoMessage.DoesNotExist:
            return None
