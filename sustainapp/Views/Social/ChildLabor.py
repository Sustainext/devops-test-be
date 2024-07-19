from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from rest_framework import serializers
from datametric.utils.analyse import set_locations_data
from datametric.utils.analyse import filter_by_start_end_dates
from logging import getLogger

logger = getLogger("error.log")


class ChildLabourAnalyzeView(APIView):

    permission_classes = [IsAuthenticated]

    def process_childlabor(self, path):

        child_labour = DataPoint.objects.filter(
            locale__in=self.locations,  # .values_list("name", flat=True),
            path__slug=path,
            client_id=self.clients_id,
        ).filter(
            filter_by_start_end_dates(start_date=self.from_date, end_date=self.to_date)
        )

        if not child_labour:
            return []

        if (
            path == "gri-social-human_rights-408-1a-1b-operations_risk_child_labour"
            or path == "gri-social-human_rights-408-1a-1b-supplier_risk_child_labor"
        ):
            necessary = ["childlabor", "TypeofOperation", "geographicareas"]
        else:
            necessary = ["hazardouswork", "TypeofOperation", "geographicareas"]
        indexed_data = {}
        for dp in child_labour:
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

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            self.from_date = serializer.validated_data["start"]
            self.to_date = serializer.validated_data["end"]

            self.organisation = serializer.validated_data["organisation"]
            self.corporate = serializer.validated_data.get("corporate", None)
            self.location = serializer.validated_data.get("location", None)

            self.clients_id = request.user.client.id

            self.locations = set_locations_data(
                organisation=self.organisation,
                corporate=self.corporate,
                location=self.location,
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

            return Response(
                {
                    "operation_significant_risk_of_child_labor": operations_childlabor,
                    "operation_significant_risk_of_young_workers": operations_young_workers,
                    "suppliers_significant_risk_of_child_labor": suppliers_childlabor,
                    "suppliers_significant_risk_of_young_workers": suppliers_young_workers,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
