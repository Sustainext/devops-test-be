from esg_report.models.ScreenTwelve import ScreenTwelve
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from esg_report.Serializer.ScreenTwelveSerializer import ScreenTwelveSerializer
from sustainapp.models import Report
from collections import defaultdict
from datametric.models import RawResponse
from esg_report.utils import (
    get_materiality_assessment,
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    collect_data_by_raw_response_and_index,
)
from datametric.utils.analyse import set_locations_data
from sustainapp.Utilities.emission_analyse import (
    get_top_emission_by_scope,
    calculate_scope_contribution,
)


class ScreenTwelveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, report_id, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_twelve: ScreenTwelve = self.report.screen_twelve
            serializer = ScreenTwelveSerializer(screen_twelve, data=request.data)
        except ObjectDoesNotExist:
            serializer = ScreenTwelveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        response_data.update(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.slugs = {
            0: "gri-environment-emissions-301-a-scope-1",
            1: "gri-environment-emissions-301-a-scope-2",
            2: "gri-environment-emissions-301-a-scope-3",
            3: "gri-environment-materials-301-1a-non_renewable_materials",
            4: "gri-environment-materials-301-1a-renewable_materials",
            5: "gri-environment-materials-301-2a-recycled_input_materials",
            6: "gri-environment-materials-301-3a-3b-reclaimed_products",
            7: "gri-environment-water-303-3a-3b-3c-3d-water_withdrawal/discharge_all_areas",
        }

    def get_303_3a_3b_3c_3d(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[7]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)
    def get_301_3a_3b(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[6]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_2a(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[5]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_1a_renewable_materials(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[4]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_1a_non_renewable_materials(self):
        local_data_points = self.data_points.filter(path__slug=self.slugs[3]).order_by(
            "index"
        )
        return collect_data_by_raw_response_and_index(data_points=local_data_points)

    def get_301_123_collect(self):
        slugs = [self.slugs[0], self.slugs[1], self.slugs[2]]
        data_points = self.data_points.filter(path__slug__in=slugs)
        slug_data = defaultdict(list)
        for slug in slugs:
            response_data = defaultdict(list)
            for data_point in data_points.filter(path__slug=slug):
                response_data[data_point.data_metric.name] = data_point.value
            slug_data[slug] = response_data
        return slug_data

    def get_301_123_analyse(self):
        locations = set_locations_data(
            organisation=self.report.organization,
            corporate=self.report.corporate,
            location=None,
        )
        top_emission_by_scope, top_emission_by_source, top_emission_by_location = (
            get_top_emission_by_scope(
                locations=locations,
                user=self.request.user,
                start=self.report.start_date,
                end=self.report.end_date,
                path_slug={
                    "gri-environment-emissions-301-a-scope-1": "Scope 1",
                    "gri-environment-emissions-301-a-scope-2": "Scope 2",
                    "gri-environment-emissions-301-a-scope-3": "Scope 3",
                },
            )
        )

        # * Prepare response data
        response_data = dict()
        response_data["all_emission_by_scope"] = calculate_scope_contribution(
            key_name="scope", scope_total_values=top_emission_by_scope
        )
        response_data["all_emission_by_source"] = calculate_scope_contribution(
            key_name="source", scope_total_values=top_emission_by_source
        )
        response_data["all_emission_by_location"] = calculate_scope_contribution(
            key_name="location", scope_total_values=top_emission_by_location
        )
        response_data["top_5_emisson_by_source"] = response_data[
            "all_emission_by_source"
        ][0:5]
        response_data["top_5_emisson_by_location"] = response_data[
            "all_emission_by_location"
        ][0:5]
        return response_data

    def get_305_4abc(self):
        # TODO: Need more clarification from Sakthivel
        return None

    def get_305_5abc(self):
        # TODO: Need more clarification from Sakthivel
        return None

    def get_3_3cde(self):
        # TODO: Materiality Assessment Screen is pending
        return None

    def get(self, request, report_id):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        response_data = {}
        try:
            screen_twelve: ScreenTwelve = self.report.screen_twelve
            serializer = ScreenTwelveSerializer(screen_twelve)
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenTwelve._meta.fields
                    if field.name not in ["id", "report"]
                }
            )

        self.set_raw_responses()
        self.set_data_points()
        response_data["3_3cde"] = self.get_3_3cde()
        response_data["305_123_collect"] = self.get_301_123_collect()
        response_data["305_123_analyse"] = self.get_301_123_analyse()
        response_data["305_4abc"] = self.get_305_4abc()
        response_data["305_5abc"] = self.get_305_5abc()
        response_data["301_1a_non_renewable_materials"] = (
            self.get_301_1a_non_renewable_materials()
        )
        response_data["301_1a_renewable_materials"] = (
            self.get_301_1a_renewable_materials()
        )
        response_data["301_2a"] = self.get_301_2a()
        response_data["301_3a_3b"] = self.get_301_3a_3b()
        return Response(response_data, status=status.HTTP_200_OK)
