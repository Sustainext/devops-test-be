from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from sustainapp.models import Report
from rest_framework.response import Response
from apps.tcfd_framework.report.models import TCFDReport
from apps.tcfd_framework.report.serializers import TCFDReportSerializer
from apps.tcfd_framework.report.services.GetTCFDReportData import GetTCFDReportData


class TCFDReportGetView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve a TCFDReport based on the report ID and screen Name.
    """

    def get(self, request, report_id, screen_name):
        try:
            tcfd_report = TCFDReport.objects.get(
                report_id=report_id, screen_name=screen_name
            )
            serializer = TCFDReportSerializer(tcfd_report)
            report_data = serializer.data["data"]
            screen_name = serializer.data["screen_name"]
            report_id = serializer.data["report"]
        except TCFDReport.DoesNotExist:
            report_data = None
        report = Report.objects.get(id=report_id)
        collect_data_object = GetTCFDReportData(report=report)
        return Response(
            data={
                "data": {
                    "report_data": report_data,
                    "screen_name": screen_name,
                    "id": report_id,
                    "tcfd_collect_data": collect_data_object.get_data_as_per_screen(
                        screen_name
                    ),
                }
            },
            status=status.HTTP_200_OK,
        )


class TCFDReportUpsertView(APIView):
    """
    Create or update a TCFDReport based on report and screen.
    Uses PUT method for upserting a report instance.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Validate input including mandatory report and screen
        serializer = TCFDReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = serializer.validated_data.get("report")
        screen_name = serializer.validated_data.get("screen_name")

        # Try to update existing object or create new one
        obj, created = TCFDReport.objects.update_or_create(
            report=report, screen_name=screen_name, defaults=serializer.validated_data
        )

        output_serializer = TCFDReportSerializer(obj)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
