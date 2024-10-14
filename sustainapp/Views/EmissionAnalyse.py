from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import set_locations_data
from sustainapp.Utilities.emission_analyse import (
    calculate_scope_contribution,
    get_top_emission_by_scope,
)


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]
    path_slug = {
        "gri-environment-emissions-301-a-scope-1": "Scope 1",
        "gri-environment-emissions-301-a-scope-2": "Scope 2",
        "gri-environment-emissions-301-a-scope-3": "Scope 3",
    }

    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing:
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate, and Year.
        """

        # * Get all the RawResponses
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]
        corporate = serializer.validated_data.get("corporate")  # * This is optional
        organisation = serializer.validated_data["organisation"]
        location = serializer.validated_data.get("location")  # * This is optional

        # * Set Locations Queryset
        locations = set_locations_data(
            organisation=organisation,
            corporate=corporate,
            location=location,
        )

        # * Get top emissions by Scope
        top_emission_by_scope, top_emission_by_source, top_emission_by_location = (
            get_top_emission_by_scope(
                locations=locations,
                request=request,
                start=start,
                end=end,
                path_slug=self.path_slug,
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
        response_data["selected_org"] = organisation.name
        response_data["selected_corporate"] = corporate.name if corporate else None
        response_data["selected_location"] = location.name if location else None
        response_data["selected_start_date"] = start
        response_data["selected_end_date"] = end

        return Response({"data": response_data}, status=status.HTTP_200_OK)
