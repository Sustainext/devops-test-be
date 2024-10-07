# views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from sustainapp.models import Organization, Corporateentity, Location
from sustainapp.Serializers.OrgCorpLocListSeroalizer import (
    CorporateSerializer,
    LocationSerializer,
)


class CorporateListView(APIView):
    """
    View to list corporates based on multiple organization IDs.
    """

    def get(self, request):
        # Get the org_ids from query parameters
        org_ids = request.query_params.get("organization_ids")

        if org_ids:
            # Split the org_ids (comma-separated string) into a list
            org_ids_list = org_ids.split(",")
            corporates = Corporateentity.objects.filter(
                client=request.user.client, organization_id__in=org_ids_list
            )
            serializer = CorporateSerializer(corporates, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No organization IDs provided"}, status=400)


class LocationListView(APIView):
    """
    View to list locations based on multiple corporate IDs.
    """

    def get(self, request):
        # Get the corporate_ids from query parameters
        corp_ids = request.query_params.get("corporate_ids")

        if corp_ids:
            # Split the corporate_ids (comma-separated string) into a list
            corp_ids_list = corp_ids.split(",")
            locations = Location.objects.filter(
                client=request.user.client, corporateentity_id__in=corp_ids_list
            )
            serializer = LocationSerializer(locations, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No corporate IDs provided"}, status=400)
