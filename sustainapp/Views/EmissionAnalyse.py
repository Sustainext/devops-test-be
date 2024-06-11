from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from django.db.models import Sum
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.db.models.fields.json import KeyTextTransform


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_scope_contribution(self, scope_total_values):
        total_emissions = sum(scope_total_values.values())
        scope_contributions = {}
        serial_number = 1

        for scope_name, scope_value in scope_total_values.items():
            contribution = (scope_value / total_emissions) * 100
            scope_contributions[scope_name] = {
                "serial_number": serial_number,
                "total": scope_value,
                "contribution": contribution,
            }

            serial_number += 1

        return scope_contributions

    def get_top_emission_by_scope(self):
        # * Get all Raw Respones based on location and year.
        self.raw_responses = RawResponse.objects.filter(
            path__slug__icontains="gri-environment-emissions-301-a-scope-",
            year=self.year,
            user=self.request.user,
        )
        self.data_points = DataPoint.objects.filter(
            raw_response__in=self.raw_responses, json_holder__isnull=False
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

        return self.calculate_scope_contribution(top_emission_by_scope)

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
        self.year = serializer.validated_data["year"]
        self.corporate = serializer.validated_data["corporate"]
        self.organisation = serializer.validated_data["organisation"]
        # * 1. Get Locations based on Corporate and Organisations.
        self.locations = self.corporate.location.all().values_list("name", flat=True)
        # * Get top emissions by Scope
        response_data = dict()
        response_data["top_emission_by_scope"] = self.get_top_emission_by_scope()
        response_data["top_emission_by_source"] = self.calculate_scope_contribution(
            self.top_emission_by_source
        )
        response_data["top_emission_by_location"] = self.calculate_scope_contribution(
            self.top_emission_by_location
        )
        return Response({"message": response_data}, status=status.HTTP_200_OK)
