from esg_report.models.ScreenThirteen import ScreenThirteen
from esg_report.Serializer.ScreenThirteenSerializer import ScreenThirteenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import Report
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_data_by_raw_response_and_index,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    get_data_by_raw_response_and_index,
)


class ScreenThirteenView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slugs = {
            0: "gri-general-workforce_employees-2-7-a-b-permanent_employee",
            1: "gri-general-workforce_employees-2-7-a-b-temporary_employee",
            3: "gri-general-workforce_employees-methodologies-2-7c",
            4: "gri-general-workforce_employees-data-2-7c",
            5: "gri-general-workforce_employees-contextual-2-7d",
            6: "gri-general-workforce_employees-fluctuations-2-7e",
        }

    def put(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            screen_thirteen = ScreenThirteen.objects.get(report=self.report)
            serializer = ScreenThirteenSerializer(screen_thirteen, data=request.data)
        except ScreenThirteen.DoesNotExist:
            serializer = ScreenThirteenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_thirteen = ScreenThirteen.objects.get(report=self.report)
            serializer = ScreenThirteenSerializer(screen_thirteen)
            response_data.update(serializer.data)
        except ScreenThirteen.DoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenThirteen._meta.fields
                    if field.name not in ["id", "report"]
                }
            )
        self.set_data_points()
        self.set_raw_responses()
        response_data["2_7_a_b_permanent_employee"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[0])
            )
        )
        response_data["2_7_a_b_temporary_employee"] = (
            collect_data_by_raw_response_and_index(
                data_points=self.data_points.filter(path__slug=self.slugs[1])
            )
        )
        response_data["2_7_c_methodologies"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[3])
        )
        response_data["2_7_c_data"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[4])
        )
        response_data["2_7_d_contextual"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[5])
        )
        response_data["2_7_e_fluctuations"] = collect_data_by_raw_response_and_index(
            data_points=self.data_points.filter(path__slug=self.slugs[6])
        )
        

        return Response(response_data, status=status.HTTP_200_OK)
