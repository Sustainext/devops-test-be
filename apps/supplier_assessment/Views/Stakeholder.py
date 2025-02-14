from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import OuterRef, Subquery, CharField, Value
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
    StakeHolderBulkDeleteSerializer,
)
from apps.supplier_assessment.pagination import SupplierAssessmentPagination
from apps.supplier_assessment.filters import StakeholderFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Concat


class StakeholderViewSet(viewsets.ModelViewSet):
    serializer_class = StakeHolderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SupplierAssessmentPagination
    filterset_class = StakeholderFilter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name", "email", "updated_at"]
    search_fields = ["name", "city", "poc", "email"]

    def get_queryset(self):
        group_id = self.request.GET.get("group_id")
        qs = StakeHolder.objects.filter(group__created_by=self.request.user)
        if group_id:
            qs = qs.filter(group_id=group_id)

        # Latest historical record (most recent)
        latest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "-history_date"
        )
        latest_name = Subquery(
            latest_history.annotate(
                full_name=Concat(
                    "history_user__first_name",
                    Value(" "),
                    "history_user__last_name",
                    output_field=CharField(),
                )
            ).values("full_name")[:1],
            output_field=CharField(),
        )
        latest_email = Subquery(
            latest_history.values("history_user__email")[:1],
            output_field=CharField(),
        )

        # Oldest historical record (creation record)
        oldest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "history_date"
        )
        oldest_name = Subquery(
            oldest_history.annotate(
                full_name=Concat(
                    "history_user__first_name",
                    Value(" "),
                    "history_user__last_name",
                    output_field=CharField(),
                )
            ).values("full_name")[:1],
            output_field=CharField(),
        )
        oldest_email = Subquery(
            oldest_history.values("history_user__email")[:1],
            output_field=CharField(),
        )

        # Annotate the queryset with these subqueries
        qs = qs.annotate(
            latest_name=latest_name,
            latest_email=latest_email,
            oldest_name=oldest_name,
            oldest_email=oldest_email,
        )
        return qs

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """
        Delete multiple StakeHolder objects.
        Expects a payload like: {"ids": [1, 2, 3]}
        """
        serializer = StakeHolderBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["ids"]
        queryset = self.get_queryset().filter(id__in=[id.id for id in ids])
        deleted_count = queryset.count()
        queryset.delete()

        return Response(
            {"detail": f"{deleted_count} stakeholder(s) deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
