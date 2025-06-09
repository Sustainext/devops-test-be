from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse # Added import
from apps.canada_bill_s211.v2.serializers.CheckYearOrganisationCorporateSerializer import CheckYearOrganizationCorporateSerializer
from apps.canada_bill_s211.v2.utils.create_excel import CanadaBillReport

class GetExcelReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CheckYearOrganizationCorporateSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data['organization']
        corporate = serializer.validated_data.get('corporate')
        year = serializer.validated_data['year']

        report_generator = CanadaBillReport(user=self.request.user,
            organization=organization,
            corporate=corporate,
            year=year)
        excel_data = report_generator.generate_excel_report_data()

        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="Canada_Bill_S211_Report_{year}.xlsx"'

        return response
