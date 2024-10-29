from esg_report.models import AboutTheCompanyAndOperations
from sustainapp.models import Report
from datametric.models import RawResponse
from esg_report.Serializer.AboutTheCompanyAndOperationsSerializer import (
    AboutTheCompanyAndOperationsSerializer,
)
from rest_framework.exceptions import NotFound
from esg_report.utils import get_latest_raw_response


class AboutTheCompanyAndOperationsService:
    def __init__(self, report_id, user):
        self.report_id = report_id
        self.user = user
        self.report = self.get_report()

    def get_report(self):
        try:
            return Report.objects.get(id=self.report_id)
        except Report.DoesNotExist:
            raise NotFound(detail="Report does not exist")

    def get_about_the_company_and_operations(self):
        try:
            about_the_company_and_operations = AboutTheCompanyAndOperations.objects.get(
                report=self.report
            )
            serializer = AboutTheCompanyAndOperationsSerializer(
                about_the_company_and_operations, context={"request": self.user}
            )
            return serializer.data
        except AboutTheCompanyAndOperations.DoesNotExist:
            return {
                "report": self.report.id,
                "about_the_company": "",
                "business_relations": "",
                "entities_included": "",
                "supply_chain_description": "",
            }

    def get_raw_responses(self):
        return RawResponse.objects.filter(
            client=self.user.client,
            year__range=(self.report.start_date.year, self.report.end_date.year),
        )

    def fetch_gri_data(self):
        # Define slugs for GRI questions
        slugs = {
            "org_details": "gri-general-org_details_2-1a-1b-1c-1d",
            "entities": "gri-general-entities-list_of_entities-2-2-a",
            "sectors": "gri-general-business_details-organisation-2-6a",
            "value_chain": "gri-general-business_details-value-2-6b",
            "relevant_business": "gri-general-business_details-other-2-6c",
            "changes": "gri-general-business_details-changes-2-6d",
        }

        raw_responses = self.get_raw_responses()
        response_data = {}

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

        return response_data

    def get_complete_report_data(self):
        about_the_company_data = self.get_about_the_company_and_operations()
        gri_data = self.fetch_gri_data()
        return {**about_the_company_data, **gri_data}
