from datametric.models import DataPoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from sustainapp.models import Corporateentity
from logging import getLogger
from common.utils.value_types import safe_percentage

logger = getLogger("error.log")


class MarketingLabelingAnalyzeView(APIView):
    """
    This is to Analyze the data for the Marketing and Labeling from the Collect/Social of the Platform
    """

    permission_classes = [IsAuthenticated]

    def process_marketing_labeling(self, path, filter_by):
        cust = DataPoint.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
        )

        req_data = {"Q1": "", "Q2": ""}
        temp_req_data = req_data.copy()
        if cust:
            # There is data for the selected Organization or Coporate
            for i in cust:
                temp_req_data[i.metric_name] = i.number_holder
            if temp_req_data["Q1"] == "" or temp_req_data["Q2"] == "":
                logger.info(
                    f"Marketing and Labeling Analyze : User has not added required data"
                )
                return []
        elif not cust and self.corp is None:
            # There is no data added for Organization and hence checking for it's corporates
            logger.info(
                f"Customer Health Analyze : There is no data for the organization {self.org} and the path {path} and the year {self.year}, So proceeding to check for its Corporates"
            )
            corps_of_org = Corporateentity.objects.filter(organization__id=self.org.id)
            cust = DataPoint.objects.filter(
                organization__id=self.org.id,
                corporate__in=corps_of_org,
                path__slug=path,
                client_id=self.client_id,
                year=self.year,
            )
            res = []
            # filtering the data as per corporate
            for a_corp in corps_of_org:
                temp_req_data_2 = req_data.copy()
                k = cust.filter(corporate=a_corp)
                if k:
                    for i in k:
                        temp_req_data_2[i.metric_name] = i.number_holder
                    if temp_req_data_2["Q1"] == "" or temp_req_data_2["Q2"] == "":
                        logger.info(
                            f"Customer Health Analyze : Either the user has selected NO or the user missed to add required data "
                        )
                    else:
                        res.append(
                            {
                                "org_or_corp": a_corp.name,
                                "number_of_products_with_procedurs": temp_req_data_2[
                                    "Q2"
                                ],
                                "number_of_products_category": temp_req_data_2["Q1"],
                                "percentage": safe_percentage(
                                    temp_req_data_2["Q2"], temp_req_data_2["Q1"]
                                ),
                            }
                        )
            return res
        else:
            # There is no data added
            return []

        return [
            {
                "org_or_corp": self.corp.name if self.corp else self.org.name,
                "number_of_products_with_procedurs": temp_req_data["Q2"],
                "number_of_products_category": temp_req_data["Q1"],
                "percentage": safe_percentage(temp_req_data["Q2"], temp_req_data["Q1"]),
            }
        ]

    def get(self, request):
        """What if they have added the data in corporate but not organization.
        Then we'll not show data for the organization"""
        serialized_data = CheckOrgCoprDateSerializer(data=request.query_params)
        serialized_data.is_valid(raise_exception=True)
        try:
            self.org = serialized_data.validated_data["organisation"]
            self.corp = serialized_data.validated_data.get("corporate", None)
            self.from_date = serialized_data.validated_data["start"]
            self.to_date = serialized_data.validated_data["end"]

            if self.from_date.year == self.to_date.year:
                self.year = self.from_date.year
            else:
                logger.info(
                    "Marketing and Labeling error: Start and End year should be same."
                )
                return Response(
                    {"error": "Start and End year should be same."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.client_id = request.user.client.id

            filter_by = {}

            filter_by["organization__id"] = self.org.id

            if self.corp is not None:
                filter_by["corporate__id"] = self.corp.id
            else:
                filter_by["corporate__id"] = None

            marketing_labeling_percent = self.process_marketing_labeling(
                "gri-social-product_labeling-417-1b-number", filter_by
            )

            return Response(
                {"marketing_labeling": marketing_labeling_percent},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.info(
                f"An error occured while analyzing Marketing and Labeling : {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
