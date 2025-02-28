from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from sustainapp.Utilities.emission_analyse import (
    calculate_scope_contribution,
    get_top_emission_by_scope,
)
from datametric.models import DataPoint
from datametric.utils.analyse import (
    filter_by_start_end_dates,
    get_raw_response_filters,
    set_locations_data,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)
from common.utils.value_types import safe_divide


class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]
    path_slug = {
        "gri-environment-emissions-301-a-scope-1": "Scope 1",
        "gri-environment-emissions-301-a-scope-2": "Scope 2",
        "gri-environment-emissions-301-a-scope-3": "Scope 3",
    }

    def __init__(self):
        super().__init__()
        self.slugs = {
            0: "gri-environment-emissions-GHG-emission-reduction-initiatives",
            1: "gri-environment-emissions-GHG emission-intensity",
        }

    def set_data_points(self):
        self.data_points = (
            DataPoint.objects.filter(path__slug__in=list(self.slugs.values()))
            .filter(client_id=self.request.user.client.id)
            .filter(
                get_raw_response_filters(
                    corporate=self.corporate, organisation=self.organization
                )
            )
            .filter(filter_by_start_end_dates(start_date=self.start, end_date=self.end))
        )

    def disclosure_analyze_305_5(self):
        data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[0])
        )
        form_data = [entry for item in data for entry in item["formData"]]
        results = []
        for data in form_data:
            initiative_taken = data.get("Q2", None)
            method = data.get("Q3", None)
            others_method = data.get("customUnit", None)
            base_year_or_base_inline = data.get("Q4", None)
            year_dict = data.get("Q5", None)
            rationale = data.get("Q6", None)
            ghg_emission_reduced = data.get("Q7", None)
            scopes = data.get("Q8", None)
            gases_included = data.get("Q9", None)
            assumption_or_calculation = data.get("Q10", None)

            if method == "Other (please specify)":
                method = others_method

            year = f"{year_dict['start']} - {year_dict['end']}" if year_dict else None
            results.append(
                {
                    "initiative_taken": initiative_taken,
                    "method": method,
                    "base_year_or_base_inline": base_year_or_base_inline,
                    "year": year,
                    "rationale": rationale,
                    "ghg_emission_reduced": ghg_emission_reduced,
                    "scopes": scopes,
                    "gases_included": gases_included,
                    "assumption_or_calculation": assumption_or_calculation,
                }
            )
        return results

    def validate_gases_constituent(self):
        ch4 = n2o = co2 = False

        for data in self.gases_data:
            if not isinstance(data, dict):
                continue

            if not ch4 and data.get("ch4", None) is not None and data.get("ch4", 0) > 0:
                ch4 = True
            if not n2o and data.get("n2o", None) is not None and data.get("n2o", 0) > 0:
                n2o = True
            if not co2 and data.get("co2", None) is not None and data.get("co2", 0) > 0:
                co2 = True

            # If all gases are found, break early
            if ch4 and n2o and co2:
                break

        return ch4, n2o, co2

    def ghg_emission_intensity(self):
        raw_data = collect_data_by_raw_response_and_index(
            self.data_points.filter(path__slug=self.slugs[1])
        )
        if not self.top_emission_by_scope:
            return []

        results = []
        emission = self.top_emission_by_scope
        total_emission = sum(emission.values()) / 1000
        ch4, n2o, co2 = self.validate_gases_constituent()
        for data in raw_data:
            organization_metric = data.get("MetricType", None)
            other_metric = data.get("customMetricType", None)
            quantity = data.get("Quantity", None)
            unit = data.get("Units", None)
            other_metric_unit = data.get("customUnit", None)
            type_of_ghg = data.get("intensityratio", None)
            organization_metric = data.get("MetricType", None)

            ghg_emission_intensity = safe_divide(total_emission, quantity)

            if organization_metric == "Other (please specify)":
                organization_metric = other_metric
                unit = other_metric_unit
            ghg_intensity_unit = f"tCO2e/{unit}"
            results.append(
                {
                    "organization_metric": organization_metric,
                    "quantity": quantity,
                    "unit": unit,
                    "type_of_ghg": type_of_ghg,
                    "ghg_emission_intensity": ghg_emission_intensity,
                    "ghg_intensity_unit": ghg_intensity_unit,
                    "ch4": ch4,
                    "n2o": n2o,
                    "co2": co2,
                    "HFCs": False,
                    "PFCs": False,
                    "SF6": False,
                    "NF3": False,
                }
            )
        return results

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
        self.organization = organisation
        self.corporate = corporate
        self.start = start
        self.end = end
        if self.corporate:
            self.organization = None

        self.set_data_points()

        # * Set Locations Queryset
        locations = set_locations_data(
            organisation=organisation,
            corporate=corporate,
            location=location,
        )

        # * Get top emissions by Scope
        (
            top_emission_by_scope,
            top_emission_by_source,
            top_emission_by_location,
            gases_data,
        ) = get_top_emission_by_scope(
            locations=locations,
            user=self.request.user,
            start=start,
            end=end,
            path_slug=self.path_slug,
        )
        self.top_emission_by_scope = top_emission_by_scope
        self.gases_data = gases_data
        disclosure_analyze_305_5 = self.disclosure_analyze_305_5()
        ghg_emission_intensity = self.ghg_emission_intensity()

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
        response_data["disclosure_analyze_305_5"] = disclosure_analyze_305_5
        response_data["ghg_emission_intensity"] = ghg_emission_intensity
        response_data["selected_org"] = organisation.name
        response_data["selected_corporate"] = corporate.name if corporate else None
        response_data["selected_location"] = location.name if location else None
        response_data["selected_start_date"] = start
        response_data["selected_end_date"] = end

        return Response({"data": response_data}, status=status.HTTP_200_OK)
