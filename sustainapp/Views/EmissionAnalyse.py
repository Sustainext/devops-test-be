from datametric.models import DataPoint, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from operator import itemgetter

from django.db.models import Prefetch
from rest_framework import serializers


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_scope_contribution(self, key_name, scope_total_values):
        total_emissions = sum(scope_total_values.values())
        scope_contributions = []
        for scope_name, scope_value in scope_total_values.items():
            contribution = (scope_value / total_emissions) * 100
            scope_contributions.append(
                {
                    key_name: scope_name,
                    "total": scope_value,
                    "contribution": round(contribution, 2),
                    "Units": "tC02e",
                }
            )
        scope_contributions.sort(key=itemgetter("contribution"), reverse=True)
        return scope_contributions

    def set_locations_data(self):
        """
        If Organisation is given and Corporate and Location is not given, then get all corporate locations
        If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
        If Location is given, then get only that location
        """
        if self.organisation and self.corporate and self.location:
            self.locations = Location.objects.filter(id=self.location.id)
        elif self.location is None and self.corporate and self.organisation:
            self.locations = self.corporate.location.all()
        elif self.location is None and self.corporate is None and self.organisation:
            self.locations = Location.objects.prefetch_related(
                Prefetch(
                    "corporateentity",
                    queryset=self.organisation.corporatenetityorg.all(),
                )
            )
        else:
            raise serializers.ValidationError(
                "Not send any of the following fields: organisation, corporate, location"
            )

    def get_top_emission_by_scope(self):
        # * Get all Raw Respones based on location and year.
        self.data_points = DataPoint.objects.filter(
            path__slug__icontains="gri-environment-emissions-301-a-scope-",
            json_holder__isnull=False,
            year__range=(self.start.year, self.end.year),
            month__range=(self.start.month, self.end.month),
            user_id=self.request.user.id,
            location__in=self.locations.values_list("name", flat=True),
        ).select_related("raw_response")
        # * Get contribution of each path in raw_responses and sum the json_holder
        top_emission_by_scope = defaultdict(lambda: 0)
        self.top_emission_by_source = defaultdict(lambda: 0)
        self.top_emission_by_location = defaultdict(lambda: 0)
        for data_point in self.data_points:
            top_emission_by_scope[data_point.raw_response.path.slug] += sum(
                [i.get("co2e", 0) for i in data_point.json_holder]
            )
            self.top_emission_by_location[data_point.location] += sum(
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
        self.set_locations_data()
        # * Get top emissions by Scope
        response_data = dict()
        response_data["top_emission_by_scope"] = self.get_top_emission_by_scope()
        response_data["top_emission_by_source"] = self.calculate_scope_contribution(
            key_name="source", scope_total_values=self.top_emission_by_source
        )
        response_data["top_emission_by_location"] = self.calculate_scope_contribution(
            key_name="location", scope_total_values=self.top_emission_by_location
        )
        return Response({"data": response_data}, status=status.HTTP_200_OK)
