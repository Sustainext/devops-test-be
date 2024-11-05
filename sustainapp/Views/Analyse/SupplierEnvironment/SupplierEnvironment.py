from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from sustainapp.Utilities.supplier_environment_analyse import (
    new_suppliers,
    calculate_percentage,
)
from logging import getLogger

logger = getLogger("error.log")


class SupplierEnvAnlayzeView(APIView):

    permission_classes = [IsAuthenticated]

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
                    "Analyze Environment > Suppliers Environmental Assessment : Start and End year should be same."
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
                filter_by_corp = True
            else:

                filter_by["corporate__id"] = None
                filter_by_corp = False

            supplier_env_data = {}

            supplier_env_data["gri_308_1a"] = new_suppliers(
                org=self.org,
                corp=self.corp,
                client_id=self.request.user.client.id,
                year=self.year,
                path="gri-supplier_environmental_assessment-new_suppliers-308-1a",
                filter_by=filter_by,
                filter_for_corp=filter_by_corp,
            )

            supplier_env_data["gri_308_2d"] = new_suppliers(
                org=self.org,
                corp=self.corp,
                client_id=self.request.user.client.id,
                year=self.year,
                path="gri-supplier_environmental_assessment-negative_environmental-308-2d",
                filter_by=filter_by,
                filter_for_corp=filter_by_corp,
            )

            supplier_env_data["gri_308_2e"] = new_suppliers(
                org=self.org,
                corp=self.corp,
                client_id=self.request.user.client.id,
                year=self.year,
                path="gri-supplier_environmental_assessment-negative_environmental-308-2e",
                filter_by=filter_by,
                filter_for_corp=filter_by_corp,
            )

            return Response(
                supplier_env_data,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"An error occured while analyzing Environment > Suppliers Environmental Assessment : {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
