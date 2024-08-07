from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates

class SupplierSocialAssessmentView(APIView):
    def get_data(self, year, client_id, filter_by):
        dp_data = DataPoint.objects.filter(
            path__slug="gri-social-supplier_screened-414-1a-number_of_new_suppliers",
            client_id=client_id,
            year=year,
            **filter_by
        )
        pos_data = DataPoint.objects.filter(
            path__slug="gri-social-impacts_and_actions-414-2a-2d-2e-negative_social_impacts",
            client_id=client_id,
            year=year,
            **filter_by
        ) 
        return dp_data, pos_data

    def get_social_data(self, data_points):
        new_supplier_data = defaultdict(lambda: 0.0)
        metric_mapping = {
            "Q1": "total_new_suppliers",
            "Q2": "total_suppliers",
        }

        for data in data_points:
            metric_key = metric_mapping.get(data.metric_name)
            if metric_key:
                new_supplier_data[metric_key] += float(data.number_holder)

        total_new_suppliers = new_supplier_data["total_new_suppliers"]
        total_suppliers = new_supplier_data["total_suppliers"]
        new_supplier_data["percentage"] = (total_new_suppliers / total_suppliers) * 100 if total_suppliers > 0 else 0

        return new_supplier_data
    
    def get_pos_data(self, data_points):
        pos = defaultdict(lambda: 0.0)
        metric_mapping = {
            "Q1": "total_number_of_negative_suppliers",
            "Q2": "total_number_of_improved_suppliers",
            "Q3": "total_number_of_suppliers_assessed",
        }

        for data in data_points:
            metric_key = metric_mapping.get(data.metric_name)
            if metric_key:
                pos[metric_key] += float(data.number_holder)

        total_number_of_negative_suppliers = pos["total_number_of_negative_suppliers"]
        total_number_of_improved_suppliers = pos["total_number_of_improved_suppliers"]
        total_number_of_suppliers_assessed = pos["total_number_of_suppliers_assessed"]

        pos["percentage_negative"] = (total_number_of_negative_suppliers / total_number_of_suppliers_assessed) * 100 if total_number_of_suppliers_assessed > 0 else 0
        pos["percentage_improved"] = (total_number_of_improved_suppliers / total_number_of_suppliers_assessed) * 100 if total_number_of_suppliers_assessed > 0 else 0

        return pos
    
    def filter_non_zero_values(self, data):
        return {k: v for k, v in data.items() if v != 0.0}
    
    def get(self, request, format=None):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        organisation = serializer.validated_data.get("organisation")
        corporate = serializer.validated_data.get("corporate")
        self.start = serializer.validated_data["start"]
        self.end = serializer.validated_data["end"]
        client_id = self.request.user.client.id

        if self.start.year == self.end.year:
            year = self.start.year
        else:
            return Response(
                {"error": "Start and End year should be same."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dp, pos = {}, {}
        filter_by = {}

        if corporate:
            filter_by['corporate'] = corporate
        elif organisation:
            filter_by['organization'] = organisation

        if filter_by:
            dp_data, pos_data = self.get_data(year, client_id, filter_by)
            dp = self.get_social_data(dp_data)
            pos = self.get_pos_data(pos_data)

        final = {
            "new_suppliers_that_were_screened_using_social_criteria": self.filter_non_zero_values(dp),
            "negative_social_impacts_in_the_supply_chain_and_actions_taken": self.filter_non_zero_values(pos),
        }

        return Response(final, status=status.HTTP_200_OK)