from sustainapp.Serializers.TaskdashboardRetriveSerializer import (
    TaskDashboardCustomSerializer,
    ClientTaskDashboardSerializer,
)
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import PermissionDenied


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserTaskDashboardView(ListAPIView):
    serializer_class = ClientTaskDashboardSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        locations = user.locs.all()
        if not (user.is_client_admin or user.is_superuser):
            raise PermissionDenied("You don't have permission access this")

        queryset = ClientTaskDashboard.objects.filter(
            (Q(location__in=locations) | Q(location__isnull=True)) & Q(assigned_by=user)
        ).order_by("-created_at")
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                Q(task_name__icontains=search_query)
                | Q(assigned_to__first_name__icontains=search_query)
                | Q(location__name=search_query)
                | Q(location__corporateentity__name__icontains=search_query)
                | Q(
                    location__corporateentity__organization__name__icontains=search_query
                )
            )

        # Check for date range filters in query parameters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        deadline_start = self.request.query_params.get("deadline_start")
        deadline_end = self.request.query_params.get("deadline_end")
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                start_date = make_aware(
                    timezone.datetime.combine(start_date, timezone.datetime.min.time())
                )
                queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                end_date = make_aware(
                    timezone.datetime.combine(end_date, timezone.datetime.max.time())
                )
                queryset = queryset.filter(created_at__lte=end_date)

        if deadline_start:
            deadline_start = parse_date(deadline_start)
            if deadline_start:
                deadline_start = make_aware(
                    timezone.datetime.combine(
                        deadline_start, timezone.datetime.min.time()
                    )
                )
                queryset = queryset.filter(deadline__gte=deadline_start)

        if deadline_end:
            deadline_end = parse_date(deadline_end)
            if deadline_end:
                deadline_end = make_aware(
                    timezone.datetime.combine(
                        deadline_end, timezone.datetime.max.time()
                    )
                )
                queryset = queryset.filter(deadline__lte=deadline_end)
        if (
            start_date is None
            and end_date is None
            and deadline_start is None
            and deadline_end is None
        ):
            past_30_days = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=past_30_days)

        assigned_to_param = self.request.query_params.get("assigned_to")
        if assigned_to_param:
            # Split the parameter into a list of IDs
            assigned_to_ids = [
                int(id) for id in assigned_to_param.split(",") if id.isdigit()
            ]
            queryset = queryset.filter(assigned_to__in=assigned_to_ids)

        status_param = self.request.query_params.get("status")
        if status_param:
            status_multi = [status for status in status_param.split(",")]
            queryset = queryset.filter(task_status__in=status_multi)

        # Filter tasks based on assignee or assigner being the current user
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Get the category from query parameters
        category = request.query_params.get("activetab", None)
        if not category:
            raise ValidationError("activetab parameter is required.")

        # Apply category-specific filters
        now = timezone.now()
        if category == "upcoming":
            queryset = queryset.filter(
                Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    deadline__gte=now,
                )
                | Q(assigned_to__isnull=True)
            )
        elif category == "overdue":
            queryset = queryset.filter(
                task_status__in=["in_progress", "not_started"],
                deadline__lt=now,
            )
        elif category == "completed":
            queryset = queryset.filter(task_status__in=["approved", "completed"])

        elif category == "for_review":
            queryset = queryset.filter(
                task_status="under_review", assigned_by=request.user
            )
        else:
            raise ValidationError(f"Invalid category: {category}")

        # Paginate and serialize the filtered queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TaskDashboardCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskDashboardCustomSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
