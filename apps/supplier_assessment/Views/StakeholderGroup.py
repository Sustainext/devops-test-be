from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup
from apps.supplier_assessment.Serializer.StakeHolderGroupSerializer import (
    StakeHolderGroupSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from apps.supplier_assessment.filters import StakeHolderGroupFilter
from rest_framework.filters import OrderingFilter
from apps.supplier_assessment.pagination import SupplierAssessmentPagination

from django.db.models import Count, Q, F

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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StakeHolderGroupFilter
    ordering_fields = ["name", "created_at", "organization__name"]
    pagination_class = SupplierAssessmentPagination

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
            StakeHolderGroup.objects.annotate(
                stakeholder_count=Count("stake_holder"),
                creator_first_name=F("created_by__first_name"),
                creator_last_name=F("created_by__last_name"),
            )
            .filter(
                created_by__client=request.user.client,
                organization__in=request.user.orgs.all(),
            )
            .filter(
                Q(corporate_entity__in=request.user.corps.all())
                | Q(corporate_entity__isnull=True)
            )
            .select_related("organization", "created_by")
            .prefetch_related("corporate_entity")
        ).order_by("id")
        filtered_groups = self.filterset_class(
            request.GET, queryset=stakeholder_groups
        ).qs
        for backend in self.filter_backends:
            filtered_groups = backend().filter_queryset(request, filtered_groups, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_groups, request)

        serializer = StakeHolderGroupSerializer(
            page, many=True, context={"request": request}
        )
        response_data = serializer.data
        for index, group in enumerate(page):
            response_data[index]["stakeholder_count"] = group.stakeholder_count

        return paginator.get_paginated_response(response_data)

    def delete(self, request, pk):
        try:
            stakeholder_group = StakeHolderGroup.objects.get(
                id=pk, created_by__client=self.request.user.client
            )
            stakeholder_group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StakeHolderGroup.DoesNotExist:
            return Response(
                {"detail": "Stakeholder group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class StakeholderGroupEditAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            stakeholder_group = (
                StakeHolderGroup.objects.filter(
                    created_by__client=request.user.client,
                    organization__in=request.user.orgs.all(),
                    corporate_entity__in=request.user.corps.all(),
                )
                .distinct()
                .get(pk=pk)
            )
            serializer = StakeHolderGroupSerializer(
                stakeholder_group,
                data=request.data,
                context={"request": request},
                partial=True,
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StakeHolderGroup.DoesNotExist:
            return Response(
                {"detail": "Stakeholder group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
