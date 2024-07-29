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


class ForcedLaborAnalyzeView(APIView):
    def get_forced_labor_data(
        self,
        location,
        start,
        end,
        path_slug,
        client_id,
    ):
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

        data_points = DataPoint.objects.filter(
            locale__in=location,
            path__slug=path_slug,
            client_id=client_id,
        ).filter(filter_by_start_end_dates(start_date=start, end_date=end))

        for data in data_points:
            if data.metric_name in metric_categories:
                key = (
                    data.index,
                    data.year,
                    data.month,
                )
                forced_labor_data[key][data.metric_name] = data.value

        unique_entries = {}
        for entry in forced_labor_data.values():
            identifier = (entry.get("TypeofOperation"), entry.get("geographicareas"))
            if identifier not in unique_entries:
                unique_entries[identifier] = entry

        results = list(unique_entries.values())

        return results

    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data["organisation"]
        corporate = serializer.validated_data.get("corporate", None)
        location = serializer.validated_data.get("location", None)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]

        if location:
            locations = Location.objects.filter(pk=location.id)
        elif corporate:
            locations = Location.objects.filter(corporateentity=corporate)
        elif organisation:
            corporate_entity = Corporateentity.objects.filter(
                organization_id=organisation.id
            ).values_list("id", flat=True)
            locations = Location.objects.filter(corporateentity__in=corporate_entity)
        else:
            return Response(
                {"error": "Please provide either organisation, corporate or location"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        location_names = locations  # .values_list("name", flat=True)

        forced_labor_operations = self.get_forced_labor_data(
            location_names,
            start,
            end,
            "gri-social-human_rights-409-1a-operations_forced_labor",
            request.user.client_id,
        )
        forced_labor_suppliers = self.get_forced_labor_data(
            location_names,
            start,
            end,
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
