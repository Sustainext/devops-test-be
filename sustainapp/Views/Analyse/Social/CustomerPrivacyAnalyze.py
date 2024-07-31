from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from datametric.utils.analyse import filter_by_start_end_dates
from logging import getLogger

logger = getLogger("error.log")


class CustomerPrivacyAnalyzeView(APIView):

    permission_classes = [IsAuthenticated]

    def process_customer_privacy(self, path):

        cust = DataPoint.objects.filter(
            organization__id=self.org,
            corporate__id=self.corp,
            path__slug=path,
            client_id=self.client_id,
        ).filter(
            filter_by_start_end_dates(start_date=self.from_date, end_date=self.to_date)
        )

        if not cust:
            return []

        necessary = ["customerprivacy", "substantiatedorganization", "regulatorybodies"]

        indexed_data = {}
        for dp in cust:
            idx = indexed_data.setdefault(dp.raw_response.id, {})
            if dp.metric_name in necessary:
                idx.setdefault(dp.index, {})[dp.metric_name] = dp.value
            else:
                logger.info(
                    f"Customer Privacy Analyze : The metric name {dp.metric_name} is not in the necessary list"
                )

        grouped_data = []
        for i_val in indexed_data.values():
            for v in i_val.values():
                temp_data = {
                    "customerprivacy": v["customerprivacy"],
                    "substantiatedorganization": v["substantiatedorganization"],
                    "regulatorybodies": v["regulatorybodies"],
                }
                if temp_data not in grouped_data:
                    grouped_data.append(temp_data)

        return grouped_data

    def get(self, request):
        """What if they have added the data in corporate but not organization.
        Then we'll not show data for the organization"""
        serialized_data = CheckOrgCoprDateSerializer(data=request.query_params)
        serialized_data.is_valid(raise_exception=True)
        try:
            self.org = serialized_data.validated_data["organisation"].id
            self.corp = serialized_data.validated_data.get("corporate", None)
            self.from_date = serialized_data.validated_data["start"]
            self.to_date = serialized_data.validated_data["end"]

            self.client_id = request.user.client.id

            if self.corp is not None:
                self.corp = self.corp.id

            customer_privacy_data = self.process_customer_privacy(
                "gri-social-customer_privacy-418-1a-total_number"
            )

            return Response(
                {"customer_privacy_data": customer_privacy_data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
