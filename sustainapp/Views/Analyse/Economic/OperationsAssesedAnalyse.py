from datametric.models import DataPoint, RawResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from sustainapp.models import Corporateentity
from logging import getLogger
from common.utils.value_types import safe_percentage

logger = getLogger("error.log")


class OperationsAssessedAnalyzeView(APIView):
    """
    This is to Analyze the data for the Operations Assessed from Anti Corruptions of Economic
    """

    permission_classes = [IsAuthenticated]

    def process_operations_assessed(self, path, filter_by):
        oa_data = DataPoint.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
        )

        req_data = {"Q1": "", "Q2": ""}
        temp_req_data = req_data.copy()
        if oa_data:
            # There is data for the selected Organization or Coporate
            for i in oa_data:
                temp_req_data[i.metric_name] = i.number_holder
            if temp_req_data["Q1"] == "" or temp_req_data["Q2"] == "":
                logger.error(
                    f"General/Collective Bargaining Analyze : User has not added required data"
                )
                return []
        elif not oa_data and self.corp is None:
            # There is no data added for Organization and hence checking for it's corporates
            logger.error(
                f"General/Collective Bargaining Analyze: There is no data for the organization {self.org} and the path {path} and the year {self.year}, So proceeding to check for its Corporates"
            )
            corps_of_org = Corporateentity.objects.filter(organization__id=self.org.id)
            oa_data = DataPoint.objects.filter(
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
                k = oa_data.filter(corporate=a_corp)
                if k:
                    for i in k:
                        temp_req_data_2[i.metric_name] = i.number_holder
                    if temp_req_data_2["Q1"] == "" or temp_req_data_2["Q2"] == "":
                        logger.error(
                            f"Economic > Anti Corruption > Operations Assessed : Either the user has selected NO or the user missed to add required data "
                        )
                    else:
                        res.append(
                            {
                                "org_or_corp": a_corp.name,
                                "total_number_of_operations_assesed": temp_req_data_2[
                                    "Q1"
                                ],
                                "number_of_operations": temp_req_data_2["Q2"],
                                "percentage": safe_percentage(
                                    temp_req_data_2["Q1"], temp_req_data_2["Q2"]
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
                "total_number_of_operations_assesed": temp_req_data["Q1"],
                "number_of_operations": temp_req_data["Q2"],
                "percentage": safe_percentage(temp_req_data["Q1"], temp_req_data["Q2"]),
            }
        ]

    def get(self, request):
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
                logger.error(
                    "Anti Corruption > Operations Assesed error: Start and End year should be same."
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

            operations_assesed_percent = self.process_operations_assessed(
                "gri-economic-operations_assessed_for_risks_related_to_corruption-205-1a-total",
                filter_by,
            )

            return Response(
                {"operations_assesed": operations_assesed_percent},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"An error occured while analyzing Economic > Anti Corruption > Operations Assessed: {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
