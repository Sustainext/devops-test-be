from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from django.db.models import OuterRef, Subquery, CharField
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
        group_id = self.request.GET.get("group_id")
        qs = StakeHolder.objects.all()
        if group_id:
            qs = qs.filter(group_id=group_id)

        # Build subqueries for audit fields using django-simple-history.
        # Latest (most recent) historical record
        latest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "-history_date"
        )
        latest_user = Subquery(
            latest_history.values("history_user__username")[:1],
            output_field=CharField(),
        )

        # Oldest historical record (i.e. creation record)
        oldest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "history_date"
        )
        oldest_user = Subquery(
            oldest_history.values("history_user__username")[:1],
            output_field=CharField(),
        )

        # Annotate the StakeHolder queryset with audit information
        qs = qs.annotate(
            created_by=oldest_user,
            last_updated_by=latest_user,
        )
        return qs