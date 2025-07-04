from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import OuterRef, Subquery, CharField, Value
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
    DeleteIDsSerializer,
)
from apps.supplier_assessment.pagination import SupplierAssessmentPagination
from apps.supplier_assessment.filters import StakeholderFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger("custom_logger")


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
        qs = StakeHolder.objects.filter(
            group__created_by__client=self.request.user.client
        )
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

    @action(detail=False, methods=["get"], url_path="historical-users")
    def historical_users(self, request):
        """
        Returns a list of distinct users who have updated the StakeHolder model.
        """
        # Retrieve distinct historical user IDs from the StakeHolder history
        stakeholder_qs = self.get_queryset()
        stakeholder_ids = stakeholder_qs.values_list("id", flat=True)
        historical_user_ids = (
            StakeHolder.history.exclude(history_user__isnull=True)
            .filter(id__in=stakeholder_ids)
            .values_list("history_user_id", flat=True)
            .distinct()
        )
        # Get the corresponding user objects
        user_model = get_user_model()
        users = user_model.objects.filter(id__in=historical_user_ids).only(
            "id", "first_name", "last_name", "email"
        )

        # Serialize minimal user data (id, first_name, last_name, email)
        user_data = [
            {
                "id": user.id,
                "full_name": user.get_full_name(),
                "email": user.email,
            }
            for user in users
        ]
        return Response(user_data)

    @action(detail=False, methods=["delete"], url_path="delete-many")
    def delete_many(self, request, *args, **kwargs):
        """
        Delete StakeHolder instances based on a list of IDs provided in the request body.
        Example request body:
            {
                "ids": [1, 2, 3]
            }
        """
        # Validate the incoming data using the serializer
        serializer = DeleteIDsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ids = serializer.validated_data["ids"]
        # Filter the queryset to the objects matching the provided IDs
        queryset = self.get_queryset().filter(id__in=ids)
        if not queryset.exists():
            return Response(
                {"error": "No matching records found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete the filtered instances
        deleted_count, _ = queryset.delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        # Ensure the incoming data is a list
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of StakeHolder objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        created_instances = (
            serializer.save()
        )  # Uses bulk_create via the custom ListSerializer.
        response_serializer = self.get_serializer(created_instances, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
