from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from esg_report.Serializer.CeoMessageSerializer import CeoMessageSerializer
from esg_report.models.ScreenOne import CeoMessage
from sustainapp.models import Report
from esg_report.services.screen_one_service import CeoMessageService


class ScreenOneView(APIView):
    """
    This API is used to get and update the CEO message
    that is the whole screen one for an ESG Report.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request, esg_report_id):
        """
        This API is used to update the CEO message for an ESG Report.
        """
        try:
            esg_report = Report.objects.get(id=esg_report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "ESG Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # * This put method will either create or update the CEO message for an ESG Report.

        serializer = CeoMessageSerializer(data=request.data)
        try:
            ceo_message = CeoMessage.objects.get(report=esg_report)
            serializer = CeoMessageSerializer(ceo_message, request.data)

        except CeoMessage.DoesNotExist:
            pass
        serializer.is_valid(raise_exception=True)
        serializer.save(report=esg_report)
        esg_report.last_updated_by = request.user
        esg_report.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, esg_report_id):
        """
        This API is used to get the CEO message for an ESG Report.
        """
        try:
            report = CeoMessageService.get_report_by_id(esg_report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Use the service to get the CEO message for the report
        ceo_message = CeoMessageService.get_ceo_message_by_report(report)
        if not ceo_message:
            return Response(None, status=status.HTTP_200_OK)

        # Return the serialized CEO message data
        return Response(
            CeoMessageSerializer(ceo_message).data, status=status.HTTP_200_OK
        )
