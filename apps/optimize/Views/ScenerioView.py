from ..models.OptimizeScenario import Scenerio
from ..Serializers.ScenarioScerializer import ScenerioSerializer
from rest_framework import viewsets
from ..Paginations.ScenarioPagination import ScenerioPaginatio


class ScenerioView(viewsets.ModelViewSet):
    serializer_class = ScenerioSerializer
    pagination_class = ScenerioPaginatio

    def get_queryset(self):
        user_orgs = self.request.user.orgs.values_list("id", flat=True)
        final_queryset = Scenerio.objects.filter(
            organization_id__in=user_orgs
        ).order_by("-created_at")
        return final_queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
