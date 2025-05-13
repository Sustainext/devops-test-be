from rest_framework.response import Response
from rest_framework import status
from esg_report.models.ScreenTwo import AboutTheCompanyAndOperations
from esg_report.Serializer.AboutTheCompanyAndOperationsSerializer import (
    AboutTheCompanyAndOperationsSerializer,
)
from esg_report.utils import get_latest_raw_response, get_raw_responses_as_per_report
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from sustainapp.models import Report


class ScreenTwo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id, format=None):
        try:
            # Fetch report
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist as e:
            return Response(
                {"error": "Report does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        # Fetch AboutTheCompanyAndOperations for the report
        try:
            about_the_company_and_operations = AboutTheCompanyAndOperations.objects.get(
                report=report
            )
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_the_company_and_operations, context={"request": request}
            )
            response_data = serializer.data
        except AboutTheCompanyAndOperations.DoesNotExist as e:
            response_data = {
                "report": report.id,
                "about_the_company": "",
                "business_relations": "",
                "entities_included": "",
                "supply_chain_description": "",
            }

        # Define slugs for GRI questions
        slugs = {
            "org_details": "gri-general-org_details_2-1a-1b-1c-1d",
            "entities": "gri-general-entities-list_of_entities-2-2-a",
            "entities_audited": "gri-general-entities-audited-2-2-b",  # 2-2-b
            "entities_multiple": "gri-general-entities-multiple-2-2-c",  # 2-2-c
            "sectors": "gri-general-business_details-organisation-2-6a",
            "value_chain": "gri-general-business_details-value-2-6b",
            "relevant_business": "gri-general-business_details-other-2-6c",
            "changes": "gri-general-business_details-changes-2-6d",
        }

        # Fetch all raw responses once, filter by the year range and client
        raw_responses = get_raw_responses_as_per_report(report=report)

        # Fetch raw responses and update the response data
        raw_response_org_details = get_latest_raw_response(
            raw_responses=raw_responses, slug=slugs["org_details"]
        )
        if raw_response_org_details:
            try:
                response_data["2-1"] = {
                    "legal_name": raw_response_org_details.data[0]["Q1"]["text"],
                    "nature_of_ownership_and_legal_form": raw_response_org_details.data[
                        0
                    ]["Q2"]["text"],
                    "location_of_headquarters": raw_response_org_details.data[0]["Q3"][
                        "text"
                    ],
                    "countries_of_operation": [
                        i["text"]
                        for i in raw_response_org_details.data[0]["Q4"]["rows"]
                    ],
                }
            except KeyError:
                response_data["2-1"] = None
        else:
            response_data["2-1"] = None

        raw_response_entities = get_latest_raw_response(
            raw_responses, slugs["entities"]
        )
        if raw_response_entities:
            response_data["2-2-a"] = [
                entity["Q1"] for entity in raw_response_entities.data
            ]
        else:
            response_data["2-2-a"] = None

        raw_response_sectors = get_latest_raw_response(
            raw_responses=raw_responses, slug=slugs["sectors"]
        )
        if raw_response_sectors:
            response_data["2-6-a"] = raw_response_sectors.data
        else:
            response_data["2-6-a"] = None

        raw_response_value_chain = get_latest_raw_response(
            raw_responses=raw_responses, slug=slugs["value_chain"]
        )
        if raw_response_value_chain:
            response_data["2-6-b"] = raw_response_value_chain.data[0]
        else:
            response_data["2-6-b"] = None

        raw_response_relevant_business = get_latest_raw_response(
            raw_responses=raw_responses, slug=slugs["relevant_business"]
        )
        if raw_response_relevant_business:
            response_data["2-6-c"] = raw_response_relevant_business.data[0]["Q1"]
        else:
            response_data["2-6-c"] = None

        raw_response_change_information = get_latest_raw_response(
            raw_responses=raw_responses, slug=slugs["changes"]
        )
        if raw_response_change_information:
            response_data["2-6-d"] = raw_response_change_information.data[0]["Q1"]
        else:
            response_data["2-6-d"] = None

        # ================================================    
        # 2-2-b: Audited, consolidated financial statements (Yes/No + Explanation)
        raw_response_entities_audited = get_latest_raw_response(
            raw_responses, slugs["entities_audited"]
        )
        if raw_response_entities_audited and raw_response_entities_audited.data:
            data = raw_response_entities_audited.data[0]
            response_data["2-2-b"] = {
                "answer": data.get("Q1", None),
                "explanation": data.get("Q2", None),
            }
        else:
            response_data["2-2-b"] = {"answer": None, "explanation": None}

        # 2-2-c: Multiple entities (Yes/No + Explanation)
        raw_response_entities_multiple = get_latest_raw_response(
            raw_responses, slugs["entities_multiple"]
        )
        if raw_response_entities_multiple and raw_response_entities_multiple.data:
            data = raw_response_entities_multiple.data[0]
            response_data["2-2-c"] = {
                "answer": data.get("Q1", None),
                "explanation": data.get("Q2", None),
            }
        else:
            response_data["2-2-c"] = {"answer": None, "explanation": None}
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, report_id, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist as e:
            return Response(
                {"Report Does Not Exist for the given parameter": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            about_the_company_and_operations = AboutTheCompanyAndOperations.objects.get(
                report=report
            )
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_the_company_and_operations, data=request.data
            )
        except AboutTheCompanyAndOperations.DoesNotExist as e:
            serializer = AboutTheCompanyAndOperationsSerializer(
                data=request.data, context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        report.last_updated_by = request.user
        report.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
