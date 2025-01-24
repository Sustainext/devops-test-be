from sustainapp.models import MyGoalOrganization
from rest_framework import viewsets
from sustainapp.Serializers.MyGoalsOrganizationSerializer import (
    MyGoalsOrganizationSerializer,
)
from rest_framework.response import Response


class MyGoalOrganizationView(viewsets.ModelViewSet):
    serializer_class = MyGoalsOrganizationSerializer

    def get_queryset(self):
        client = self.request.user.client
        organizations = self.request.user.orgs.all()
        return MyGoalOrganization.objects.filter(
            client=client, organization__in=organizations
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=request.user.client, created_by=request.user)
        return Response(serializer.data, status=201)
