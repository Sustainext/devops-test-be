from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class GetEmissionAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Returns a dictionary with keys containing
        1. Top Emission by Scope
        2. Top Emission by Source
        3. Top Emission by Location
        filtered by Organisation, Corporate and Year"""

    

