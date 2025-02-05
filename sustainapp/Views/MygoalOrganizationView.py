from sustainapp.models import MyGoalOrganization
from rest_framework import viewsets
from sustainapp.Serializers.MyGoalsOrganizationSerializer import (
    MyGoalsOrganizationSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from authentication.Permissions.isSuperuserAndClientAdmin import IsAdmin


class MyGoalOrganizationView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing MyGoalOrganization instances.
    Pemrissions for this view(Add, Edit, Delete):
    - Superuser
    - Admin
    - ClientAdmin
    Users linked to an organization will be able to see organization specific goals
    Only Authenticated users can access this view
    """

    serializer_class = MyGoalsOrganizationSerializer

    def get_permissions(self):
        if (
            self.action == "list" or self.action == "retrieve"
        ):  # This will use Global Permissions defined in settings.py
            return super().get_permissions()
        else:
            return [
                permission() for permission in [IsAdmin]
            ]  # All other actions will use this custom permission(Superuser, Admin, ClientAdmin)

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
