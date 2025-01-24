from sustainapp.models import MyGoalOrganization
from rest_framework import viewsets
from sustainapp.Serializers.MyGoalsOrganizationSerializer import (
    MyGoalsOrganizationSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


class MyGoalOrganizationView(viewsets.ModelViewSet):
    serializer_class = MyGoalsOrganizationSerializer

    def get_queryset(self):
        client = self.request.user.client
        organizations = self.request.user.orgs.all()
        return MyGoalOrganization.objects.filter(
            client=client, organization__in=organizations
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Organize your tasks based on some attributes
        tasks = {
            "upcoming": queryset.filter(status__in=["not_started", "in_progress"]),
            "overdue": queryset.filter(
                status__in=["not_started", "in_progress"], deadline__lt=timezone.now()
            ),
            "completed": queryset.filter(status="completed"),
        }
        serialized_data = {
            category: MyGoalsOrganizationSerializer(
                tasks[category], many=True, context={"request": request}
            ).data
            for category in tasks
        }

        return Response(serialized_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=request.user.client, created_by=request.user)
        return Response(serializer.data, status=201)
