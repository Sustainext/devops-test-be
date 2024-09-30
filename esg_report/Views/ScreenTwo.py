from rest_framework.response import Response
from rest_framework import status
from datametric.models import RawResponse, Path
from esg_report.models.ScreenTwo import AboutTheCompanyAndOperations
from esg_report.Serializer.AboutTheCompanyAndOperationsSerializer import (
    AboutTheCompanyAndOperationsSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from sustainapp.models import Report


class GetAboutTheCompanyAndOperations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report, format=None):
        try:
            report = Report.objects.get(id=report)
            about_the_company_and_operations = AboutTheCompanyAndOperations.objects.get(
                report=report
            )
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_the_company_and_operations
            )
            about_the_company_and_operations_data = serializer.data
            response_data = {
                "about_the_company_and_operations": about_the_company_and_operations_data[
                    "about_the_company"
                ],
            
            }
            # * GRI 2-1-a, 2-1-b, 2-1-c, 2-1-d
            slugs = [
                
            ]
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
