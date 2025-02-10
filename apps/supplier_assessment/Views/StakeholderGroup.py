from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup
from apps.supplier_assessment.Serializer.StakeHolderGroupSerializer import (
    StakeHolderGroupSerializer,
)
from django.db.models import Count

"""
*APIs to create

1. Create Stakeholder Group
2. Get List of Every Stakeholder Group by created_by
"""


class StakeholderGroupAPI(APIView):
    """
    This class handles the creation of a new StakeHolderGroup.
    It requires the user to be authenticated, and uses the StakeHolderGroupSerializer to validate and save the new group, associating it with the requesting user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StakeHolderGroupSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        stakeholder_groups = (
            StakeHolderGroup.objects.annotate(stakeholder_count=Count("stake_holder"))
            .filter(created_by=request.user)
            .select_related("organization")
            .prefetch_related("corporate_entity")
        )
        serializer = StakeHolderGroupSerializer(
            stakeholder_groups, many=True, context={"request": request}
        )
        response_data = serializer.data
        for index, group in enumerate(stakeholder_groups):
            response_data[index]["stakeholder_count"] = group.stakeholder_count

        return Response(response_data)
