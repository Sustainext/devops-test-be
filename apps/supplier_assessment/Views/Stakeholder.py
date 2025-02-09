from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
)


class StakeholderViewSet(viewsets.ModelViewSet):
    serializer_class = StakeHolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs.get("group_id")
        if group_id:
            return StakeHolder.objects.filter(
                group_id=group_id, group__created_by=self.request.user
            )
        return StakeHolder.objects.filter(group__created_by=self.request.user)
