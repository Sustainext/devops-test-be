from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datametric.models import Path, RawResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.serializers import ValidationError
from esg_report.models import ESGReport


class GetAboutTheCompanyOperationsInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id: int, format=None):
        slug = "gri-general-about_the_company-2-1-describe"
        try:
            esg_report = ESGReport.objects.get(id=report_id)
        except ESGReport.DoesNotExist:
            raise ValidationError("Give Report ID is not valid")
        try:
            raw_response_data = RawResponse.objects.filter(
                client=self.request.user.client, year=esg_report.end_date.year
            ).get(path__slug=slug)
            return Response(raw_response_data.data, status=status.HTTP_200_OK)
        except RawResponse.DoesNotExist:
            raise NotFound([])
