from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates
from sustainapp.Utilities.supplier_social_assessment_analyse import (
    filter_non_zero_values,
    get_data,
    get_pos_data,
    get_social_data,
)


class SupplierSocialAssessmentView(APIView):

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
            filter_by["corporate"] = corporate
        elif organisation:
            filter_by["organization"] = organisation

        if filter_by:
            dp_data, pos_data = get_data(year, client_id, filter_by)
            dp = get_social_data(dp_data)
            pos = get_pos_data(pos_data)

        final = {
            "new_suppliers_that_were_screened_using_social_criteria": filter_non_zero_values(
                dp
            ),
            "negative_social_impacts_in_the_supply_chain_and_actions_taken": filter_non_zero_values(
                pos
            ),
        }

        return Response(final, status=status.HTTP_200_OK)
