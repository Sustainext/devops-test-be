from ..models.OptimizeScenario import Scenerio
from ..Serializers.ScenarioScerializer import ScenerioSerializer
from rest_framework import viewsets
from ..Paginations.ScenarioPagination import ScenerioPagination
from ..models.BusinessMetric import BusinessMetric
from ..filters import ScenarioFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status


class ScenarioView(viewsets.ModelViewSet):
    """This class defines the view for the Scenerio model.
    It uses the ScenerioSerializer for serialization and deserialization,
    and the ScenerioPagination for pagination.
    It also uses DjangoFilterBackend, OrderingFilter, and SearchFilter for filtering and ordering.
    """

    serializer_class = ScenerioSerializer
    pagination_class = ScenerioPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ScenarioFilter
    ordering_fields = ["name"]
    search_fields = ["name"]

    def get_queryset(self):
        user_orgs = self.request.user.orgs.values_list("id", flat=True)
        final_queryset = Scenerio.objects.filter(
            organization_id__in=user_orgs
        ).order_by("-created_at")
        return final_queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        scenario_name = instance.name

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": f"Scenario '{scenario_name}' created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        scenario_name = instance.name
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "message": f"Scenario '{scenario_name}' updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        # add validation here if scenario by corporate then corporate is required
        scenario = serializer.save(
            created_by=self.request.user, updated_by=self.request.user
        )
        BusinessMetric.objects.create(scenario=scenario)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        scenario_name = instance.name
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": f"Scenario '{scenario_name}' deleted successfully."}, status=204
        )
