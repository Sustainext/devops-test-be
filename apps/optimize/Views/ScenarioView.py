from ..models.OptimizeScenario import Scenerio
from ..Serializers.ScenarioScerializer import ScenerioSerializer
from rest_framework import viewsets
from ..Paginations.ScenarioPagination import ScenerioPagination
from ..models.BusinessMetric import BusinessMetric


class ScenarioView(viewsets.ModelViewSet):
    serializer_class = ScenerioSerializer
    pagination_class = ScenerioPagination

    def get_queryset(self):
        user_orgs = self.request.user.orgs.values_list("id", flat=True)
        final_queryset = Scenerio.objects.filter(
            organization_id__in=user_orgs
        ).order_by("-created_at")
        return final_queryset

    def perform_create(self, serializer):
        # add validation here if scenario by corporate then corporate is required
        scenario = serializer.save(
            created_by=self.request.user, updated_by=self.request.user
        )
        BusinessMetric.objects.create(scenario=scenario)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
