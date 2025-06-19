from esg_report.models import AboutTheCompanyAndOperations
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.Serializer.AboutTheCompanyAndOperationsSerializer import (
    AboutTheCompanyAndOperationsSerializer,
)
from rest_framework.exceptions import NotFound
from esg_report.utils import get_latest_raw_response
from common.utils.report_datapoint_utils import get_raw_responses_as_per_report
from django.shortcuts import get_object_or_404


class ScreenTwoService:
    def __init__(self, user):
        self.user = user

    def get_screen_two_data(self, report_id, request):
        """
        Fetch and construct the complete data for Screen Two.
        Combines AboutTheCompanyAndOperations data and extracted raw responses.
        """
        # Step 1: Fetch the report
        report = self.fetch_report(report_id)

        # Step 2: Fetch AboutTheCompanyAndOperations data
        about_company, is_new = self.fetch_about_company(report)
        response_data = self.get_about_company_data(about_company, report, request)

        # Step 3: Define slugs for raw responses
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

        # Step 4: Fetch raw responses
        raw_responses = self.fetch_raw_responses(report)

        # Step 5: Use extract_data to process raw responses
        extracted_data = self.extract_data(raw_responses, slugs)

        # Step 6: Merge extracted data into the response
        response_data.update(extracted_data)

        return response_data

    def fetch_report(self, report_id):
        """Fetch a report by its ID or raise a 404 error."""
        return get_object_or_404(Report, id=report_id)

    def fetch_about_company(self, report):
        """Fetch AboutTheCompanyAndOperations object for a report."""
        try:
            instance = AboutTheCompanyAndOperations.objects.get(report=report)
            return instance, False  # Instance exists
        except AboutTheCompanyAndOperations.DoesNotExist:
            return None, True  # Instance does not exist

    def get_about_company_data(self, about_company, report, request):
        """Serialize the AboutTheCompanyAndOperations data or return a default structure."""
        if about_company:
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_company, context={"request": request}
            )
            return serializer.data
        return {
            "report": report.id,
            "about_the_company": "",
            "business_relations": "",
            "entities_included": "",
            "supply_chain_description": "",
        }

    def fetch_raw_responses(self, report):
        """Fetch all relevant raw responses for the user."""
        return get_raw_responses_as_per_report(report=report)

    def extract_data(self, raw_responses, slugs):
        """Extract and map raw response data based on specified slugs."""
        response_data = {}

        # Extract data for organizational details
        response_data["2-1"] = self._extract_organizational_details(
            raw_responses, slugs["org_details"]
        )

        # Extract data for other slugs
        response_data["2-2-a"] = self._fetch_raw_response_data(
            raw_responses, slugs["entities"], key="Q1", list_response=True
        )

        
        raw_2_2_b = self._fetch_raw_response_data(raw_responses, slugs["entities_audited"])
        response_data["2-2-b"] = {
            "answer": raw_2_2_b[0].get("Q1") if raw_2_2_b else None,
            "explanation": raw_2_2_b[0].get("Q2") if raw_2_2_b else None,
        }

        raw_2_2_c = self._fetch_raw_response_data(raw_responses, slugs["entities_multiple"])
        response_data["2-2-c"] = {
            "answer": raw_2_2_c[0].get("Q1") if raw_2_2_c else None,
            "explanation": raw_2_2_c[0].get("Q2") if raw_2_2_c else None,
        }


        response_data["2-6-a"] = self._fetch_raw_response_data(
            raw_responses, slugs["sectors"]
        )
        response_data["2-6-b"] = self._fetch_raw_response_data(
            raw_responses, slugs["value_chain"], index=0
        )
        response_data["2-6-c"] = self._fetch_raw_response_data(
            raw_responses, slugs["relevant_business"], key="Q1", index=0
        )
        response_data["2-6-d"] = self._fetch_raw_response_data(
            raw_responses, slugs["changes"], key="Q1", index=0
        )

        return response_data

    def _extract_organizational_details(self, raw_responses, slug):
        """Extract organizational details from raw responses."""
        raw_response = get_latest_raw_response(raw_responses=raw_responses, slug=slug)
        if raw_response:
            try:
                return {
                    "legal_name": raw_response.data[0]["Q1"]["text"],
                    "nature_of_ownership_and_legal_form": raw_response.data[0]["Q2"][
                        "text"
                    ],
                    "location_of_headquarters": raw_response.data[0]["Q3"]["text"],
                    "countries_of_operation": [
                        row["text"] for row in raw_response.data[0]["Q4"]["rows"]
                    ],
                }
            except (KeyError, IndexError):
                return None
        return None

    def _fetch_raw_response_data(
        self, raw_responses, slug, key=None, list_response=False, index=None
    ):
        """Helper method to fetch raw response data for a given slug."""
        raw_response = get_latest_raw_response(raw_responses=raw_responses, slug=slug)
        if raw_response:
            try:
                if key and index is not None:
                    return raw_response.data[index].get(key)
                elif key:
                    return (
                        [item[key] for item in raw_response.data]
                        if list_response
                        else raw_response.data[0].get(key)
                    )
                else:
                    return (
                        raw_response.data[index]
                        if index is not None
                        else raw_response.data
                    )
            except (KeyError, IndexError):
                return None
        return None
