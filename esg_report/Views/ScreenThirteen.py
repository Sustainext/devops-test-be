from esg_report.models.ScreenThirteen import ScreenThirteen
from esg_report.Serializer.ScreenThirteenSerializer import ScreenThirteenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import Report
from esg_report.services.screen_thirteen_service import ScreenThirteenService
from rest_framework.permissions import IsAuthenticated


class ScreenThirteenView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def put(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            screen_thirteen = ScreenThirteen.objects.get(report=self.report)
            serializer = ScreenThirteenSerializer(
                screen_thirteen,
                data=request.data,
                partial=True,
                context={"request": request},
            )
        except ScreenThirteen.DoesNotExist:
            serializer = ScreenThirteenSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        screen_thirteen_service = ScreenThirteenService(
            report_id=report_id, request=request
        )
        response_data = screen_thirteen_service.get_api_response()

        return Response(response_data, status=status.HTTP_200_OK)
