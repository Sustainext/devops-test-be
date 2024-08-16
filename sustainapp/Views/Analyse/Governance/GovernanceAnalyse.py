from datametric.models import RawResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class GovernanceAnalyse(APIView):
    permission_classes = [IsAuthenticated]

    slugs = [""]

    def get(self, request, format=None): ...
