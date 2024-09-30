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


class ScreenTwo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
            about_the_company_and_operations = AboutTheCompanyAndOperations.objects.get(
                report=report
            )
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_the_company_and_operations
            )
            about_the_company_and_operations_data = serializer.data
            response_data = about_the_company_and_operations_data
            # * GRI 2-1-a, 2-1-b, 2-1-c, 2-1-d
            slugs = [
                "gri-general-org_details_2-1a-1b-1c-1d",
                "gri-general-entities-list_of_entities-2-2-a",
                "gri-general-business_details-organisation-2-6a",
                "gri-general-business_details-value-2-6b",
                "gri-general-business_details-other-2-6c",
                "gri-general-business_details-changes-2-6d",
            ]
            raw_responses = RawResponse.objects.filter(
                client=self.request.user.client
            ).filter(year__range=(report.start_date.year, report.end_date.year))

            raw_response_org_details = raw_responses.filter(path__slug=slugs[0]).latest(
                "year"
            )
            response_data["2-1"] = {
                "legal_name": raw_response_org_details.data[0]["Q1"]["text"],
                "nature_of_ownership_and_legal_form": raw_response_org_details.data[0][
                    "Q2"
                ]["text"],
                "location_of_headquarters": raw_response_org_details.data[0]["Q3"][
                    "text"
                ],
                "countries_of_operation": [
                    i["text"] for i in raw_response_org_details.data[0]["Q4"]["rows"]
                ],
            }

            raw_response_entities = raw_responses.filter(path__slug=slugs[1]).latest(
                "year"
            )
            raw_response_entities_data = []
            for data in raw_response_entities.data:
                raw_response_entities_data.append(data["Q1"])
            response_data["2-2-a"] = raw_response_entities_data
            raw_response_sectors = raw_responses.filter(path__slug=slugs[2]).latest(
                "year"
            )
            response_data["2-6-a"] = raw_response_sectors.data
            raw_response_value_chain = raw_responses.filter(path__slug=slugs[3]).latest(
                "year"
            )
            response_data["2-6-b"] = raw_response_value_chain.data

            raw_response_relevant_business = raw_responses.filter(
                path__slug=slugs[4]
            ).latest("year")
            response_data["2-6-c"] = raw_response_relevant_business.data[0]["Q1"]

            raw_response_change_information = raw_responses.filter(
                path__slug=slugs[5]
            ).latest("year")
            response_data["2-6-d"] = raw_response_change_information.data[0]["Q1"]
            return Response(response_data, status=status.HTTP_200_OK)

        except Report.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
            serializer = AboutTheCompanyAndOperationsSerializer(data=request.data)
            if serializer.is_valid():
                AboutTheCompanyAndOperations.objects.filter(report=report).delete()
                serializer.save(report=report)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Report.DoesNotExist as e:
            return Response(
                {"Report Does Not Exist for the given parameter": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
