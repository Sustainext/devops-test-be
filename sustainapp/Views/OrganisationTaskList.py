from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from sustainapp.Serializers.TaskdashboardRetriveSerializer import (
    ClientTaskDashboardSerializer,
    ClientTaskDashboardBulkUpdateSerializer,
)
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from sustainapp.signals import task_status_changed
from sustainapp.celery_tasks.send_mail import (
    send_bulk_approved_and_reject_emails,
    send_bulk_task_emails,
)
from logging import getLogger

logger = getLogger("celery_logger")


class OrganisationTaskDashboardView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientTaskDashboardSerializer

    def get_queryset(self):
        user = self.request.user
        # Filter tasks based on assignee or assigner being the current user
        return ClientTaskDashboard.objects.filter(
            Q(assigned_to=user) | Q(assigned_by=user)
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        completed_statuses = ["approved", "completed"]
        # Organize your tasks based on some attributes
        tasks = {
            "upcoming": queryset.filter(
                Q(
                    task_status__in=["in_progress", "reject", "not_started"],
                    assigned_to=request.user,
                )
                | Q(
                    task_status__in=["in_progress", "reject", "not_started"],
                    assigned_by=request.user,
                    assigned_to__isnull=True,
                )
            ).exclude(deadline__lt=timezone.now()),
            "overdue": queryset.filter(
                Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    assigned_to=request.user,
                    deadline__lt=timezone.now(),
                )
                | Q(
                    task_status__in=["in_progress", "not_started", "reject"],
                    assigned_by=request.user,
                    assigned_to__isnull=True,
                    deadline__lt=timezone.now(),
                )
            ),
            "completed": queryset.filter(
                Q(task_status__in=completed_statuses, assigned_to=request.user)
                | Q(
                    task_status__in=completed_statuses,
                    assigned_by=request.user,
                    assigned_to__isnull=True,
                )
            ),
            "for_review": queryset.filter(
                task_status="under_review", assigned_by=request.user
            ),
        }

        # Serialize data with custom context for each task category
        serialized_data = {
            category: ClientTaskDashboardSerializer(
                tasks[category], many=True, context={"request": request}
            ).data
            for category in tasks
        }

        return Response(serialized_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Custom Create method to handle bulk Task creation"""

        if isinstance(request.data, list):
            task_data = request.data
        else:
            task_data = [request.data]

        tasks_to_create = []
        serializer = self.get_serializer(data=task_data, many=True)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        for validated_data in serializer.validated_data:
            tasks_to_create.append(
                ClientTaskDashboard(**validated_data, assigned_by=user)
            )

        # Bulk create the tasks
        created_tasks = ClientTaskDashboard.objects.bulk_create(tasks_to_create)

        # Fetch created task IDs (Bulk create doesn't return them immediately)
        created_task_ids = [task.pk for task in created_tasks]

        # Store initial task status in cache
        for task in created_tasks:
            cache_key_task_status = f"original_task_status_{task.pk}"
            cache.set(cache_key_task_status, task.task_status, timeout=60)

        logger.info(f"Queuing Celery Email Task for Task IDs: {created_task_ids}")

        # Send all emails asynchronously in one Celery task
        send_bulk_task_emails.apply_async(args=[created_task_ids], countdown=2)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assigned_by != request.user:
            raise PermissionDenied("You do not have permission to delete this task.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["patch"], url_path="bulk-update")
    def bulk_update(self, request, *args, **kwargs):
        """Handles bulk update of tasks dynamically using serializer-defined fields"""
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate data using the serializer
        serializer = ClientTaskDashboardBulkUpdateSerializer(
            data=request.data, many=True, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Extract valid task IDs safely
        task_ids = [
            data.get("id") for data in validated_data if data.get("id") is not None
        ]

        if not task_ids:
            return Response(
                {"error": "No valid 'id' fields provided for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch tasks from DB that match provided IDs
        tasks = {
            task.id: task
            for task in ClientTaskDashboard.objects.filter(id__in=task_ids)
        }

        updated_tasks = []
        approved_task = []
        for data in validated_data:
            task_id = data.get("id")
            task = tasks.get(task_id)

            if not task:
                continue  # Ignore invalid task IDs

            # Ensure only the assigner can update the task
            if task.assigned_by != request.user:
                return Response(
                    {"error": f"You do not have permission to update task {task.id}"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            comments = next(
                (
                    item.get("comments", "")
                    for item in request.data
                    if item.get("id") == task_id
                ),
                "",
            )
            # Capture previous values
            previous_status = task.task_status
            previous_assigned_to = task.assigned_to
            # Apply the updates dynamically
            for key, value in data.items():
                if key != "id":  # Avoid updating ID
                    setattr(task, key, value)

            updated_tasks.append(task)
            cache_key_task_status = f"original_task_status_{task.pk}"
            cache_key_assigned_to = f"original_assigned_to_{task.pk}"
            cache.set(cache_key_task_status, previous_status, timeout=60)
            cache.set(cache_key_assigned_to, previous_assigned_to, timeout=60)
            if task.task_status != previous_status and (
                task.task_status == "reject" or task.task_status == "in_progress"
            ):
                task_status_changed.send(
                    sender=task.__class__, instance=task, comments=comments
                )
            if task.task_status != previous_status and task.task_status == "approved":
                approved_task.append(task.id)

        if approved_task:
            logger.info(f"Queuing Celery Email Task for Task IDs: {approved_task}")
            send_bulk_approved_and_reject_emails.apply_async(
                args=[approved_task], countdown=2
            )

        # Dynamically get the updatable fields (excluding 'id')
        model_fields = [
            field.name
            for field in ClientTaskDashboard._meta.fields
            if field.name != "id"
        ]

        # Perform bulk update dynamically
        if updated_tasks:
            ClientTaskDashboard.objects.bulk_update(updated_tasks, model_fields)

        # Serialize and return updated tasks
        response_serializer = ClientTaskDashboardSerializer(updated_tasks, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
