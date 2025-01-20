from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import ClientTaskDashboard
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from sustainapp.Serializers.TaskdashboardRetriveSerializer import (
    TaskDashboardCustomSerializer,
    ClientTaskDashboardSerializer,
)
from rest_framework.exceptions import ValidationError
from sustainapp.signals import send_task_assigned_email
from django.core.cache import cache


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
                | Q(assigned_by=request.user, assigned_to__isnull=True)
            ).exclude(deadline__lt=timezone.now()),
            "overdue": queryset.filter(
                task_status="in_progress",
                assigned_to=request.user,
                deadline__lt=timezone.now(),
            ),
            "completed": queryset.filter(
                task_status__in=completed_statuses, assigned_to=request.user
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

        # After validation, prepare the task objects to be created
        for validated_data in serializer.validated_data:
            tasks_to_create.append(ClientTaskDashboard(**validated_data))

        # Bulk create the tasks
        ClientTaskDashboard.objects.bulk_create(tasks_to_create)
        # Manually trigger the post-save-like logic for each created task
        for task in tasks_to_create:
            # Retrieve the task with its newly assigned ID
            task = ClientTaskDashboard.objects.get(pk=task.pk)

            # Cache the task status, if needed
            cache_key_task_status = f"original_task_status_{task.pk}"
            cache.set(cache_key_task_status, task.task_status, timeout=60)

            # Manually trigger the email sending logic
            send_task_assigned_email(None, task, created=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserTaskDashboardView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientTaskDashboardSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = ClientTaskDashboard.objects.select_related(
            "assigned_by", "assigned_to"
        ).filter(Q(assigned_by=user))

        # Filter tasks based on assignee or assigner being the current user
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serialized_data = TaskDashboardCustomSerializer(queryset, many=True).data

        return Response(serialized_data, status=status.HTTP_200_OK)
