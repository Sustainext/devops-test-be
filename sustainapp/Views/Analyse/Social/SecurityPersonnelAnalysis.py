from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datametric.models import DataPoint, RawResponse
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
from datametric.utils.analyse import filter_by_start_end_dates
from collections import defaultdict
from logging import getLogger
from common.utils.value_types import safe_percentage

logger = getLogger("error.log")


class SecurityPersonnelAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def analyse_security_perrsonnel(self, start_date, end_date, location, path):
        # get all data points for the given path
        data_points = DataPoint.objects.filter(
            locale=location,
            path__slug=path,
            client_id=self.request.user.client.id,
        ).filter(filter_by_start_end_dates(start_date=start_date, end_date=end_date))

        if not data_points:
            return []

        indexed_data = defaultdict(lambda: defaultdict(dict))

        for dp in data_points:
            if dp.raw_response and dp.index is not None:
                # Ensure that we have a dictionary to update at each level
                indexed_data[dp.raw_response.id][dp.index].update(
                    {dp.metric_name: dp.value}
                )

        grouped_data = []
        for key, op in indexed_data.items():
            for sub_value in op.values():
                try:
                    securitypersonnel = float(sub_value.get("securitypersonnel"))
                    organization = (
                        float(sub_value.get("organization", 0))
                        if sub_value.get("organization")
                        else 0
                    )
                    thirdpartyorganizations = (
                        float(sub_value.get("thirdpartyorganizations", 0))
                        if sub_value.get("thirdpartyorganizations")
                        else 0
                    )

                    grouped_data.append(
                        {
                            "sp_in_org": (
                                safe_percentage(organization, securitypersonnel)
                            ),
                            "sp_3rd_org": (
                                safe_percentage(
                                    thirdpartyorganizations, securitypersonnel
                                )
                            ),
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error occrued while analyzing Security Personnel : {e}"
                    )
        return grouped_data

    def get(self, request):
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            start_date = serializer.validated_data["start"]
            end_date = serializer.validated_data["end"]
            location = serializer.validated_data["location"]

            security_personnel = self.analyse_security_perrsonnel(
                start_date,
                end_date,
                location,
                "gri-social-human_rights-410-1a-security_personnel",
            )

            return Response(
                {"security_personnel": security_personnel}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
