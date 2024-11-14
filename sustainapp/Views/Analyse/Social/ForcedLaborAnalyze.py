from datametric.models import DataPoint
from sustainapp.models import Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates
from logging import getLogger

logger = getLogger("error.log")

class ForcedLaborAnalyzeView(APIView):

    def call_common_code(self, path_slug, data_points):
        # Define the categories we are interested in
        if path_slug == "gri-social-human_rights-409-1a-suppliers_forced_labor":
            metric_categories = [
                "TypeofOperation",
                "geographicareas",
                "compulsorylabor",
            ]
        else:
            metric_categories = ["TypeofOperation", "geographicareas", "childlabor"]

        forced_labor_data = defaultdict(lambda: {})

        for data in data_points:
            if data.metric_name in metric_categories:
                key = (
                    data.index,
                    data.year,
                    data.month,
                )
                forced_labor_data[key][data.metric_name] = data.value
        # print(forced_labor_data)

        unique_entries = {}
        for entry in forced_labor_data.values():
            identifier = (entry.get("TypeofOperation"), entry.get("geographicareas"))
            if identifier not in unique_entries:
                unique_entries[identifier] = entry

        results = list(unique_entries.values())

        return results

    def get_forced_labor_data(
        self,
        organisation,
        corporate,
        year,
        path_slug,
        client_id,
    ):

        data_points = DataPoint.objects.filter(
            organization=organisation,
            corporate=corporate,
            path__slug=path_slug,
            client_id=client_id,
            year=year,
        )

        if not data_points:

            logger.error(
                f"No data found for Forced labour analysis for organisation {organisation}, corporate {corporate}, path {path_slug}, client id {client_id} and year {year}"
            )

            if not corporate:
                corps_of_org = Corporateentity.objects.filter(organization=organisation)
                res = []
                # filtering the data as per corporate
                for a_corp in corps_of_org:
                    forced_labour_corp_dp = DataPoint.objects.filter(
                        organization=organisation,
                        corporate=a_corp,
                        path__slug=path_slug,
                        client_id=client_id,
                        year=year,
                    )
                    res.extend(self.call_common_code(path_slug, forced_labour_corp_dp))
                return res
            return []

        return self.call_common_code(path_slug, data_points)

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data["organisation"]
        corporate = serializer.validated_data.get("corporate", None)
        # location = serializer.validated_data.get("location", None)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]

        if start.year != end.year:
            return Response(
                "Start and End dates must be in the same year",
                status=status.HTTP_400_BAD_REQUEST,
            )

        forced_labor_operations = self.get_forced_labor_data(
            organisation,
            corporate,
            start.year,
            "gri-social-human_rights-409-1a-operations_forced_labor",
            request.user.client_id,
        )
        forced_labor_suppliers = self.get_forced_labor_data(
            organisation,
            corporate,
            start.year,
            "gri-social-human_rights-409-1a-suppliers_forced_labor",
            request.user.client_id,
        )

        return Response(
            {
                "operations_considered_to_have_significant_risk_for_incidents_of_forced_or_compulsary_labor": forced_labor_operations,
                "suppliers_at_significant_risk_for_incidents_of_forced_or_compulsory_labor": forced_labor_suppliers,
            },
            status=status.HTTP_200_OK,
        )
