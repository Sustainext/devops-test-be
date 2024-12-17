import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import os
from collections import defaultdict
from common.enums.ScopeCategories import (
    CategoryMappings,
)
from sustainapp.Serializers.ClimatiqQueryParamsSerializer import (
    ClimatiqQueryParamsSerializer,
)
import logging

logger = logging.getLogger("custom_logger")


class ClimatiqDataAPIView(APIView):
    """
    This view is used to fetch the data from Climatiq Search API.
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.climatiq_api_key = os.environ.get("CLIMATIQ_AUTH_TOKEN")
        self.data_version = f"^{os.getenv('CLIMATIQ_DATA_VERSION')}"
        self.URL = f"{os.getenv('CLIMATIQ_BASE_URL')}data/v1/search"
        self.headers = {
            "Authorization": f"Bearer {self.climatiq_api_key}",
            "Content-Type": "application/json",
        }
        self.results = []
        self.climatiq_data = defaultdict(set)
        self.climatiq_data.update(
            {
                "year": set(),
                "source": list(),
                "region": list(),
                "category": set(),
                "sector": set(),
                "unit_type": set(),
                "source_lca_activity": set(),
                "access_type": set(),
                "data_quality_flags": set(),
            }
        )
        self.loop_condition = True
        self.total_pages = 0

    def set_condition_for_continueing_loop(self):
        if len(self.results) < 5:
            self.loop_condition = False

    def updating_response(self, api_response):
        self.results.extend(api_response.get("results", []))
        self.climatiq_data["year"].update(
            api_response.get("possible_filters", {}).get("year", [])
        )
        self.climatiq_data["source"].extend(
            api_response.get("possible_filters", {}).get("source", [])
        )
        self.climatiq_data["region"].extend(
            api_response.get("possible_filters", {}).get("region", [])
        )
        self.climatiq_data["unit_type"].update(
            api_response.get("possible_filters", {}).get("unit_type", [])
        )
        self.climatiq_data["source_lca_activity"].update(
            api_response.get("possible_filters", {}).get("source_lca_activity", [])
        )
        self.climatiq_data["access_type"].update(
            api_response.get("possible_filters", {}).get("access_type", [])
        )
        self.climatiq_data["data_quality_flags"].update(
            api_response.get("possible_filters", {}).get("data_quality_flags", [])
        )
        self.climatiq_data["category"].update(
            api_response.get("possible_filters", {}).get("category", [])
        )
        self.climatiq_data["sector"].update(
            api_response.get("possible_filters", {}).get("sector", [])
        )

    def fetch_all_climatiq_pages(self, params):
        """
        Fetches all pages of data from Climatiq API by checking last_page from response
        """
        all_results = []
        current_page = 1

        # Get first page to determine total pages
        params["page"] = current_page
        initial_response = self.calling_climatiq_api(params)

        if not initial_response:
            return []

        last_page = initial_response.get("last_page", 1)

        # Add results from first page
        self.updating_response(initial_response)

        # Fetch remaining pages
        while current_page < last_page:
            current_page += 1
            params["page"] = current_page
            response = self.calling_climatiq_api(params)

            if response and response.get("results"):
                self.updating_response(response)
            self.total_pages = self.total_pages + 1

        return all_results

    def calling_climatiq_api(self, params):
        # * Call climatiq API
        response = requests.get(
            params=params,
            headers={
                "Authorization": f"Bearer {self.climatiq_api_key}",
                "Content-Type": "application/json",
            },
            url=self.URL,
        ).json()
        print(f"URL: {self.URL}")
        print(f"Params: {params}")
        print(f"Response: {response}")
        return response

    def send_response(self):
        return Response(
            {
                "total_pages": self.total_pages,
                "total_results": len(self.results),
                "results": self.results,
                "filters": self.climatiq_data,
            },
            status=status.HTTP_200_OK,
        )

    def sort_results_by_private_key(self):
        self.results.sort(key=lambda x: x["access_type"])

    def get(self, request, *args, **kwargs):
        serializer = ClimatiqQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        year = serializer.validated_data["year"]
        category = serializer.validated_data["category"]
        region = serializer.validated_data["region"]
        results_per_page = 500
        params = {
            "year": year,
            "category": category,
            "region": region,
            "page": 1,
            "results_per_page": results_per_page,
            "data_version": self.data_version,
        }
        # * Base Call
        self.fetch_all_climatiq_pages(params=params)
        if len(self.results) > 5:
            self.loop_condition = False

        if self.loop_condition:  # * If we have to run the loop for region
            params["region"] = "*"
            self.fetch_all_climatiq_pages(params=params)
        if len(self.results) > 0:
            self.loop_condition = False
        if self.loop_condition:  # * If we have to run the loop for year wise data.
            # * Setback the region to the original value
            params["region"] = region
            for i in range(year, 2018, -1):
                params["year"] = i
                self.fetch_all_climatiq_pages(params=params)

        # * Finally check the category from the mappings.
        if category in CategoryMappings:
            for category_mapping in CategoryMappings[category]:
                params.update(category_mapping)
                self.fetch_all_climatiq_pages(params=params)
        # * Sort the result based whether access_type by private in ascending order.
        self.sort_results_by_private_key()
        return self.send_response()
