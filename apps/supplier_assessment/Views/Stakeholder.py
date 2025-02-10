from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
)
from apps.supplier_assessment.pagination import StakeholderPagination
from apps.supplier_assessment.filters import StakeholderFilter


class StakeholderViewSet(viewsets.ModelViewSet):
    serializer_class = StakeHolderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StakeholderPagination
    filterset_class = StakeholderFilter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "email", "updated_at"]

    def get_queryset(self):
        group_id = self.kwargs.get("group_id")
        if group_id:
            return StakeHolder.objects.filter(
                group_id=group_id, group__created_by=self.request.user
            )
        return StakeHolder.objects.filter(group__created_by=self.request.user)
