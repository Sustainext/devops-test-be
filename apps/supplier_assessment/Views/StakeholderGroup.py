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
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.supplier_assessment.pagination import SupplierAssessmentPagination

from django.db.models import Count, Q, F, OuterRef, Subquery, CharField, Value
from django.db.models.functions import Concat


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
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = StakeHolderGroupFilter
    ordering_fields = ["name", "created_at", "organization__name"]
    search_fields = [
        "name",
        "group_type",
        "created_by__first_name",
        "created_by__last_name",
        "organization__name",
        "created_by__email",
        "corporate_entity__name",
    ]
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
        latest_group_history = StakeHolderGroup.history.filter(
            id=OuterRef("id")
        ).order_by("-history_date")
        latest_updated_by_name = Subquery(
            latest_group_history.annotate(
                full_name=Concat(
                    "history_user__first_name",
                    Value(" "),
                    "history_user__last_name",
                    output_field=CharField(),
                )
            ).values("full_name")[:1],
            output_field=CharField(),
        )
        latest_updated_by_email = Subquery(
            latest_group_history.values("history_user__email")[:1],
            output_field=CharField(),
        )
        stakeholder_groups = (
            StakeHolderGroup.objects.annotate(
                stakeholder_count=Count("stake_holder"),
                creator_first_name=F("created_by__first_name"),
                creator_last_name=F("created_by__last_name"),
                updated_by_name=latest_updated_by_name,
                updated_by_email=latest_updated_by_email,
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
        ).order_by("-created_at")
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
            response_data[index]["updated_by_name"] = group.updated_by_name
            response_data[index]["updated_by_email"] = group.updated_by_email

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
                )
                .filter(
                    Q(corporate_entity__in=request.user.corps.all())
                    | Q(corporate_entity__isnull=True)
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


class StakeHolderGroupDistinctCreatedByAPI(APIView):
    """
    API view that returns a distinct list of emails from the 'created_by' field
    of all StakeHolderGroup instances for the requesting client's user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            (
                StakeHolderGroup.objects.filter(
                    created_by__client=request.user.client,
                    organization__in=request.user.orgs.all(),
                ).filter(
                    Q(corporate_entity__in=request.user.corps.all())
                    | Q(corporate_entity__isnull=True)
                )
            )
            .select_related("created_by")
            .distinct()
            .values(
                "created_by__email", "created_by__first_name", "created_by__last_name"
            )
        )
        data = [
            {
                "email": item["created_by__email"],
                "name": f"{item['created_by__first_name']} {item['created_by__last_name']}",
            }
            for item in data
        ]
        return Response(data, status=status.HTTP_200_OK)
