from datametric.models import DataPoint, Path, DataMetric, RawResponse
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import set_locations_data
from operator import itemgetter
from datametric.utils.analyse import filter_by_start_end_dates

from django.db.models import Prefetch
from rest_framework import serializers


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]
    path_slug = {
        "gri-environment-emissions-301-a-scope-1": "Scope 1",
        "gri-environment-emissions-301-a-scope-2": "Scope 2",
        "gri-environment-emissions-301-a-scope-3": "Scope 3",
    }

    def calculate_scope_contribution(self, key_name, scope_total_values):
        total_emissions = sum(scope_total_values.values())
        scope_contributions = []
        for scope_name, scope_value in scope_total_values.items():
            try:
                contribution = (scope_value / total_emissions) * 100
            except ZeroDivisionError:
                contribution = 0
            scope_contributions.append(
                {
                    key_name: scope_name,
                    "total": scope_value,
                    "contribution": round(contribution, 3),
                    "Units": "tC02e",
                }
            )
        scope_contributions.sort(key=itemgetter("contribution"), reverse=True)
        return scope_contributions

    def get_top_emission_by_scope(self):
        # * Get all Raw Respones based on location and year.
        self.data_points = DataPoint.objects.filter(
            json_holder__isnull=False,
            is_calculated=True,
            path__slug__icontains="gri-collect-emissions-scope-combined",
            locale__in=self.locations,  # .values_list("name", flat=True),
            client_id=self.request.user.client.id,
        ).select_related("raw_response").filter(
            filter_by_start_end_dates(start_date=self.start, end_date=self.end)
        )
        # * Get contribution of each path in raw_responses and sum the json_holder
        top_emission_by_scope = defaultdict(lambda: 0)
        self.top_emission_by_source = defaultdict(lambda: 0)
        self.top_emission_by_location = defaultdict(lambda: 0)
        for data_point in self.data_points:
            top_emission_by_scope[
                self.path_slug[data_point.raw_response.path.slug]
            ] += sum([i.get("co2e", 0) for i in data_point.json_holder])
            self.top_emission_by_location[data_point.locale.name] += sum(
                [i.get("co2e", 0) for i in data_point.json_holder]
            )
            for emission_request, climatiq_response in zip(
                data_point.raw_response.data, data_point.json_holder
            ):
                self.top_emission_by_source[
                    emission_request["Emission"]["Category"]
                ] += climatiq_response.get("co2e", 0)

        return self.calculate_scope_contribution(
            key_name="scope", scope_total_values=top_emission_by_scope
        )

    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate and Year"""

        # * Get all the RawResponses
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        self.corporate = serializer.validated_data.get(
            "corporate"
        )  # * This is optional
        self.organisation = serializer.validated_data["organisation"]
        self.location = serializer.validated_data.get("location")  # * This is optional
        # * Set Locations Queryset
        self.locations = set_locations_data(
            organisation=self.organisation,
            corporate=self.corporate,
            location=self.location,
        )
        # * Get top emissions by Scope
        response_data = dict()
        response_data["all_emission_by_scope"] = self.get_top_emission_by_scope()
        response_data["all_emission_by_source"] = self.calculate_scope_contribution(
            key_name="source", scope_total_values=self.top_emission_by_source
        )
        response_data["all_emission_by_location"] = self.calculate_scope_contribution(
            key_name="location", scope_total_values=self.top_emission_by_location
        )
        response_data["top_5_emisson_by_source"] = response_data["all_emission_by_source"][0:5]
        response_data["top_5_emisson_by_location"] = response_data["all_emission_by_location"][0:5]
        response_data["selected_org"] = self.organisation.name
        response_data["selected_corporate"] = self.corporate.name if self.corporate else None
        response_data["selected_location"] = self.location.name if self.location else None
        response_data["selected_start_date"] = self.start
        response_data["selected_end_date"] = self.end
        return Response({"data": response_data}, status=status.HTTP_200_OK)
