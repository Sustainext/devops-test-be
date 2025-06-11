from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.tcfd_framework.models.TCFDCollectModels import (
    CoreElements,
    RecommendedDisclosures,
    DataCollectionScreen,
)

class GetDisclosureSelection(APIView):
    """
    This view gets the core elements and recommended disclosures for TCFD Collect Section.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = []
        