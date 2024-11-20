from esg_report.models import AboutTheCompanyAndOperations
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.Serializer.AboutTheCompanyAndOperationsSerializer import (
    AboutTheCompanyAndOperationsSerializer,
)
from rest_framework.exceptions import NotFound
from esg_report.utils import get_latest_raw_response
from django.shortcuts import get_object_or_404


class ScreenTwoService:
    def __init__(self, user):
        self.user = user

    def fetch_report(self, report_id):
        """Fetch a report by its ID or raise a 404 error."""
        return get_object_or_404(Report, id=report_id)

    def fetch_about_company(self, report):
        """Fetch AboutTheCompanyAndOperations object for a report."""
        try:
            instance = AboutTheCompanyAndOperations.objects.get(report=report)
            return instance, False
        except AboutTheCompanyAndOperations.DoesNotExist:
            return None, True

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
        return RawResponse.objects.filter(
            client=self.user.client,
            year__range=(report.start_date.year, report.end_date.year),
        )

    def extract_data(self, raw_responses, slugs):
        """Extract and map raw response data based on specified slugs."""
        response_data = {}
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

        # Fetch and map additional data similarly
        response_data["2-2-a"] = self._fetch_raw_response_data(
            raw_responses, slugs["entities"], "Q1", list_response=True
        )
        response_data["2-6-a"] = self._fetch_raw_response_data(
            raw_responses, slugs["sectors"]
        )
        response_data["2-6-b"] = self._fetch_raw_response_data(
            raw_responses, slugs["value_chain"], index=0
        )
        response_data["2-6-c"] = self._fetch_raw_response_data(
            raw_responses, slugs["relevant_business"], "Q1", index=0
        )
        response_data["2-6-d"] = self._fetch_raw_response_data(
            raw_responses, slugs["changes"], "Q1", index=0
        )

        return response_data

    def _fetch_raw_response_data(
        self, raw_responses, slug, key=None, list_response=False, index=None
    ):
        """Helper method to fetch raw response data."""
        #TODO: Match with esg report api. 
        raw_response = get_latest_raw_response(raw_responses=raw_responses, slug=slug)
        if raw_response:
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
                    raw_response.data[index] if index is not None else raw_response.data
                )
        return None
