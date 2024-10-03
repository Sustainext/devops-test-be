"""
This file contains GET, PUT API for creating, updating, and getting CEO message
"""

from esg_report.models.ScreenOne import CeoMessage
from esg_report.models.ESGReport import ESGReport
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from esg_report.Serializer.CeoMessageSerializer import CeoMessageSerializer
from sustainapp.models import Report


class ScreenOneView(APIView):
    """
    This API is used to get and update the CEO message that is the whole screen one for an ESG Report.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request, esg_report_id, format=None):
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
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        message_image = serializer.validated_data["message_image"]
        ceo_name = serializer.validated_data["ceo_name"]
        company_name = serializer.validated_data["company_name"]
        ceo_message, _ = CeoMessage.objects.update_or_create(
            report=esg_report,
            defaults={
                "message": message,
                "message_image": message_image,
                "ceo_name": ceo_name,
                "company_name": company_name,
            },
        )
        ceo_message.save()
        return Response(
            CeoMessageSerializer(ceo_message).data, status=status.HTTP_200_OK
        )

    def get(self, request, esg_report_id, format=None):
        """
        This API is used to get the CEO message for an ESG Report.
        """
        try:
            report = Report.objects.get(id=esg_report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        ceo_message = CeoMessage.objects.get(report=report)
        return Response(
            CeoMessageSerializer(ceo_message).data, status=status.HTTP_200_OK
        )
