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
        completed_statuses = [1, 3]
        # Organize your tasks based on some attributes
        tasks = {
            "upcoming": queryset.filter(
                task_status__in=[0, 4], assigned_to=request.user
            ).exclude(deadline__lt=timezone.now()),
            "overdue": queryset.filter(
                task_status=0, assigned_to=request.user, deadline__lt=timezone.now()
            ),
            "completed": queryset.filter(
                task_status__in=completed_statuses, assigned_to=request.user
            ),
            "for_review": queryset.filter(task_status=2, assigned_by=request.user),
        }

        # Serialize data with custom context for each task category
        serialized_data = {
            category: ClientTaskDashboardSerializer(
                tasks[category], many=True, context={"request": request}
            ).data
            for category in tasks
        }

        return Response(serialized_data, status=status.HTTP_200_OK)


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
