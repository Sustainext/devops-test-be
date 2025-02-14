from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from django.db.models import OuterRef, Subquery, CharField, Value
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
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
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["name", "email", "updated_at"]

    def get_queryset(self):
        group_id = self.request.GET.get("group_id")
        qs = StakeHolder.objects.filter(group__created_by=self.request.user)
        if group_id:
            qs = qs.filter(group_id=group_id)

        # Latest historical record (most recent)
        latest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "-history_date"
        )
        latest_user = Subquery(
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

        # Oldest historical record (creation record)
        oldest_history = StakeHolder.history.filter(id=OuterRef("id")).order_by(
            "history_date"
        )
        oldest_user = Subquery(
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

        # Annotate the StakeHolder queryset with audit information
        qs = qs.annotate(
            created_by=oldest_user,
            last_updated_by=latest_user,
        )
        return qs

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """
        Delete multiple StakeHolder objects.
        Expects a payload like: {"ids": [1, 2, 3]}
        """
        ids = request.data.get("ids")
        if not ids or not isinstance(ids, list):
            return Response(
                {"detail": "Please provide a list of IDs to delete."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=ids)
        deleted_count = queryset.count()
        queryset.delete()

        return Response(
            {"detail": f"{deleted_count} stakeholder(s) deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
