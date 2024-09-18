from rest_framework.views import APIView
from sustainapp.Serializers.ScopeCategoriesSerializer import ScopeCategoriesSerializer
from common.enums.ScopeCategories import (
    Missing_SubCategories,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from django.conf import settings
from rest_framework.exceptions import APIException
import os


class ScopeCategoriesAPIView(APIView):
    """
    * Make the response structure as it is in climatiq.
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        self.CLIMATIQ_AUTH_TOKEN = os.getenv("CLIMATIQ_AUTH_TOKEN", "")
        self.permission_classes = [IsAuthenticated]
        self.URL = os.getenv("CLIMATIQ_BASE_URL", "") + "search"
        self.satisfied_condition = False
        self.response_data = {
            "results": [],
            "total_results": 0,
            "year": set(),
            "source": list(),
            "region": list(),
            "unit_type": set(),
            "source_lca_activity": set(),
            "access_type": set(),
            "data_quality_flags": set(),
        }
        self.response_result = dict()
        self.current_page = 1
        self.last_page = 1

    def special_categories_request(self, sub_category: str):
        if Missing_SubCategories.get(sub_category) is None:
            return
        source_and_year_list = Missing_SubCategories[sub_category]
        for source_and_year_dict in source_and_year_list:
            self.params["year"] = source_and_year_dict["year"]
            self.params["source"] = source_and_year_dict["source"]
            response = requests.get(
                params=self.params, headers=self.headers, url=self.URL
            )
            self.set_all_page_responses(json_response=response.json())

    def sorting_by_private_access_type(self):
        """
        Sorts the response data by the private access type.

        """
        # * Sort the response_data by access_type field
        self.response_data["results"].sort(key=lambda x: x["access_type"])

    def set_response_condition(self):
        private_access_type = sum(
            1
            for d in self.response_data["results"]
            if d.get("access_type") == "private"
        )
        if self.response_data["total_results"] - private_access_type <= 5:
            self.satisfied_condition = False
        else:
            self.satisfied_condition = True

    def sends_and_set_response_condition(self):
        """
        Checks if the response from the Climatiq API is valid as per our business needs or not.
        The public access type and the private access type should not be less than or equal to 5.
        """
        response = requests.get(
            params=self.params, headers=self.headers, url=self.URL
        ).json()
        if "error" in response.keys():
            raise APIException(detail=response)
        self.set_all_page_responses(json_response=response)
        self.set_response_condition()

    def setting_response_data_in_final_response(self, json_response):
        self.response_data["results"].extend(json_response["results"])
        self.response_data["year"].update(json_response["possible_filters"]["year"])
        self.response_data["source"].append(json_response["possible_filters"]["source"])

        self.response_data["region"].append(json_response["possible_filters"]["region"])
        self.response_data["unit_type"].update(
            json_response["possible_filters"]["unit_type"]
        )
        self.response_data["source_lca_activity"].update(
            json_response["possible_filters"]["source_lca_activity"]
        )
        self.response_data["access_type"].update(
            json_response["possible_filters"]["access_type"]
        )
        self.response_data["data_quality_flags"].update(
            json_response["possible_filters"]["data_quality_flags"]
        )

    def set_all_page_responses(self, json_response):
        """
        Returns all the page response of the response from the Climatiq API.
        """
        ...
        self.current_page = json_response["current_page"]
        self.last_page = json_response["last_page"]
        if self.current_page == self.last_page:
            self.setting_response_data_in_final_response(json_response=json_response)
        else:
            for page in range(self.current_page, self.last_page + 1, 1):
                self.params["page"] = page
                self.current_page = page
                response = requests.get(
                    params=self.params, headers=self.headers, url=self.URL
                )

                self.setting_response_data_in_final_response(
                    json_response=response.json()
                )
        self.response_data["total_results"] += json_response["total_results"]

    def send_response(self):
        """
        Returns the response data as per the business needs.
        """
        self.sorting_by_private_access_type()
        return Response(self.response_data, status=status.HTTP_200_OK)

    def get(self, request, format=None):

        serializer = ScopeCategoriesSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        sub_category = serializer.validated_data["sub_category"]
        year = serializer.validated_data["year"]
        year = 2023 if year >= 2024 else year
        region = (
            serializer.validated_data["region"]
            if serializer.validated_data["region"] != None
            else ""
        )
        self.headers = {
            "Authorization": f"Bearer {self.CLIMATIQ_AUTH_TOKEN}",
            "Content-type": "application/json",
        }
        self.params = {
            "region": region + "*",
            "year": int(year),
            "category": sub_category,
            "data_version": "^16",
            "results_per_page": 500,
        }
        self.sends_and_set_response_condition()
        if self.satisfied_condition:
            return self.send_response()
        self.params["region"] = "*"
        self.sends_and_set_response_condition()
        if self.satisfied_condition:
            return self.send_response()
        for i in range(year, 2018, -1):
            self.params["year"] = i
            self.sends_and_set_response_condition()
            if self.satisfied_condition:
                return self.send_response()
        self.special_categories_request(sub_category=sub_category)
        self.send_response()
