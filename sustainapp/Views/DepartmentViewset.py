from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Department
from sustainapp.Serializers.DepartmentSerializer import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users only see their own departments
        return Department.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)
