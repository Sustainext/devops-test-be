from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckAnalysisViewSerializer import CheckAnalysisViewSerializer
class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get_top_emission_by_scope(self):
        # * Get all Raw Respones based on location and year.
        raw_responses = RawResponse.objects.filter(path__slug__in="gri-environment-emissions-301-a-scope-",year=self.year)


    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate and Year"""

        # * Get all the RawResponses
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        self.year = serializer.validated_data["year"]
        self.corporate = serializer.validated_data["corporate"]
        self.organisation = serializer.validated_data["organisation"]
        # * 1. Get Locations based on Corporate and Organisations.
        # * 1.a. All the organisations of the user.
        self.locations = self.corporate.location.all().values_list("name", flat=True)

        return Response({"message": self.locations}, status=status.HTTP_200_OK)

        # * 1. Top Emission by Scope
