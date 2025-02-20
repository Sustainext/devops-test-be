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
from django.core.cache import cache
from django.utils.timezone import now
import hashlib
from sustainapp.celery_tasks.store_cache import store_cache


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
        if not (user.is_client_admin or user.is_superuser or user.admin):
            raise PermissionDenied("You don't have permission to access this")

        queryset = (
            ClientTaskDashboard.objects.select_related(
                "location",
                "assigned_to",
                "location__corporateentity",
                "location__corporateentity__organization",
            )
            .filter(
                (Q(location__in=locations) | Q(location__isnull=True))
                & Q(assigned_by=user)
            )
            .order_by("-created_at")
        )

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

        if not any([start_date, end_date, deadline_start, deadline_end]):
            past_30_days = now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=past_30_days)

        assigned_to_param = self.request.query_params.get("assigned_to")
        if assigned_to_param:
            assigned_to_ids = [
                int(id) for id in assigned_to_param.split(",") if id.isdigit()
            ]
            queryset = queryset.filter(assigned_to__in=assigned_to_ids)

        status_param = self.request.query_params.get("status")
        if status_param:
            status_multi = [status for status in status_param.split(",")]
            queryset = queryset.filter(task_status__in=status_multi)

        return queryset

    def list(self, request, *args, **kwargs):
        cache_key = self.generate_cache_key(request)

        # Fetch cache synchronously
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        queryset = self.get_queryset()
        category = request.query_params.get("activetab", None)

        if not category:
            raise ValidationError("activetab parameter is required.")

        now_time = now()
        if category == "upcoming":
            queryset = queryset.filter(
                Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    deadline__gte=now_time,
                )
                | Q(
                    task_status__in=["in_progress", "reject", "not_started"],
                    assigned_to__isnull=True,
                )
            )
        elif category == "overdue":
            queryset = queryset.filter(
                Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    deadline__lt=now_time,
                )
                | Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    assigned_to__isnull=True,
                    deadline__lt=now_time,
                )
            )
        elif category == "completed":
            queryset = queryset.filter(task_status__in=["approved", "completed"])
        elif category == "for_review":
            queryset = queryset.filter(
                task_status="under_review", assigned_by=request.user
            )
        else:
            raise ValidationError(f"Invalid category: {category}")

        # Paginate and serialize queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TaskDashboardCustomSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = TaskDashboardCustomSerializer(queryset, many=True)
            response_data = serializer.data

        # Store cache asynchronously using Celery
        store_cache.delay(
            cache_key, response_data, timeout=300
        )  # 300 seconds (5 minutes)

        return Response(response_data, status=status.HTTP_200_OK)

    def generate_cache_key(self, request):
        user_id = request.user.id
        query_params = tuple(
            sorted(request.query_params.items())
        )  # Faster tuple sorting

        query_hash = hashlib.md5(str(query_params).encode()).hexdigest()
        return f"user_{user_id}_task_dashboard_{query_hash}"
