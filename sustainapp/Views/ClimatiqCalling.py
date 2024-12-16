import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import os


class ClimatiqDataAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get query parameters from the request
        year = request.query_params.get("year")
        results_per_page = request.query_params.get("results_per_page")
        region = request.query_params.get("region")
        category = request.query_params.get("category")
        page = request.query_params.get("page")
        data_version = request.query_params.get("data_version")

        # Climatiq API endpoint
        climatiq_url = "https://api.climatiq.io/data/v1/search"

        # Headers for the Climatiq API request
        headers = {
            "Authorization": f"Bearer {os.getenv('CLIMATIQ_AUTH_TOKEN')}",
            "User-Agent": "Apidog/1.0.0 (https://apidog.com)",
            "Accept": "*/*",
        }

        # Query parameters
        params = {
            "year": year,
            "results_per_page": results_per_page,
            "region": region,
            "category": category,
            "page": page,
            "data_version": data_version,
        }

        try:
            # Make the external API request
            response = requests.get(climatiq_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
