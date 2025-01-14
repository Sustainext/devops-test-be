from datametric.models import DataPoint
from sustainapp.models import Corporateentity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from collections import defaultdict
from logging import getLogger

logger = getLogger("error.log")


class ChildLabourAndForcedLabourAnalyzeView(APIView):
    """
    This view is used to get the child labour analysis and forced labour analysis.
    """

    permission_classes = [IsAuthenticated]

    def call_commoncode(self, path, child_labour_dp):
        if (
            path == "gri-social-human_rights-408-1a-1b-operations_risk_child_labour"
            or path == "gri-social-human_rights-408-1a-1b-supplier_risk_child_labor"
        ):
            necessary = ["childlabor", "TypeofOperation", "geographicareas"]
        else:
            necessary = ["hazardouswork", "TypeofOperation", "geographicareas"]
        indexed_data = {}
        for dp in child_labour_dp:
            if dp.raw_response.id not in indexed_data:
                indexed_data[dp.raw_response.id] = {}
            if dp.metric_name in necessary:
                if dp.index not in indexed_data[dp.raw_response.id]:
                    indexed_data[dp.raw_response.id][dp.index] = {}
                indexed_data[dp.raw_response.id][dp.index][dp.metric_name] = dp.value
            else:
                logger.info(
                    f"Child Labor Analyze : The metric name {dp.metric_name} is not in the necessary list"
                )

        grouped_data = []
        for i_key, i_val in indexed_data.items():
            for k, v in i_val.items():
                if (
                    path
                    == "gri-social-human_rights-408-1a-1b-operations_risk_child_labour"
                    or path
                    == "gri-social-human_rights-408-1a-1b-supplier_risk_child_labor"
                ):
                    temp_data = {
                        "childlabor": v["childlabor"],
                        "TypeofOperation": v["TypeofOperation"],
                        "geographicareas": v["geographicareas"],
                    }
                else:
                    temp_data = {
                        "hazardouswork": v["hazardouswork"],
                        "TypeofOperation": v["TypeofOperation"],
                        "geographicareas": v["geographicareas"],
                    }
                if temp_data not in grouped_data:
                    grouped_data.append(temp_data)

        return grouped_data

    def process_childlabor(self, path):

        child_labour_dp = DataPoint.objects.filter(
            organization=self.organisation,
            corporate=self.corporate,
            path__slug=path,
            client_id=self.clients_id,
            year=self.from_date.year,
        )

        if not child_labour_dp:
            logger.error(
                f"No data found for child labour analysis for organisation {self.organisation}, corporate {self.corporate}, path {path}, client id {self.clients_id} and year {self.from_date.year}"
            )
            if not self.corporate:
                corps_of_org = Corporateentity.objects.filter(
                    organization=self.organisation
                )
                res = []
                # filtering the data as per corporate
                for a_corp in corps_of_org:
                    child_labour_corp_dp = DataPoint.objects.filter(
                        organization=self.organisation,
                        corporate=a_corp,
                        path__slug=path,
                        client_id=self.clients_id,
                        year=self.from_date.year,
                    )
                    res.extend(self.call_commoncode(path, child_labour_corp_dp))
                return res

            return []

        return self.call_commoncode(path, child_labour_dp)

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

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            self.from_date = serializer.validated_data["start"]
            self.to_date = serializer.validated_data["end"]

            self.organisation = serializer.validated_data["organisation"]
            self.corporate = serializer.validated_data.get("corporate", None)

            self.clients_id = request.user.client.id

            if self.from_date.year != self.to_date.year:
                return Response(
                    "Start and End dates must be in the same year",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            operations_childlabor = self.process_childlabor(
                "gri-social-human_rights-408-1a-1b-operations_risk_child_labour"
            )
            operations_young_workers = self.process_childlabor(
                "gri-social-human_rights-408-1a-1b-operations_young_worker_exposed"
            )
            suppliers_childlabor = self.process_childlabor(
                "gri-social-human_rights-408-1a-1b-supplier_risk_child_labor"
            )
            suppliers_young_workers = self.process_childlabor(
                "gri-social-human_rights-408-1a-1b-supplier_young_worker_exposed"
            )

            forced_labor_operations = self.get_forced_labor_data(
                self.organisation,
                self.corporate,
                self.from_date.year,
                "gri-social-human_rights-409-1a-operations_forced_labor",
                request.user.client_id,
            )
            forced_labor_suppliers = self.get_forced_labor_data(
                self.organisation,
                self.corporate,
                self.from_date.year,
                "gri-social-human_rights-409-1a-suppliers_forced_labor",
                request.user.client_id,
            )

            return Response(
                {
                    "operations_considered_to_have_significant_risk_for_incidents_of_forced_or_compulsary_labor": forced_labor_operations,
                    "suppliers_at_significant_risk_for_incidents_of_forced_or_compulsory_labor": forced_labor_suppliers,
                    "operation_significant_risk_of_child_labor": operations_childlabor,
                    "operation_significant_risk_of_young_workers": operations_young_workers,
                    "suppliers_significant_risk_of_child_labor": suppliers_childlabor,
                    "suppliers_significant_risk_of_young_workers": suppliers_young_workers,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
