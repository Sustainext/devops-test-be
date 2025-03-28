from django.core.cache import cache
from ..models.OptimizeScenario import Scenerio
from ..Serializers.ScenarioScerializer import ScenerioSerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ScenerioView(viewsets.ModelViewSet):
    serializer_class = ScenerioSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user_orgs = self.request.user.orgs.values_list("id", flat=True)
        final_queryset = Scenerio.objects.none()

        for org_id in user_orgs:
            cache_key = f"scenerio_qs_org_{org_id}"
            cached_qs = cache.get(cache_key)

            if cached_qs is not None:
                print("Cache hit for org_id:", org_id)
                final_queryset = final_queryset | cached_qs
            else:
                qs = Scenerio.objects.filter(organization_id=org_id).order_by(
                    "-created_at"
                )
                cache.set(cache_key, qs, timeout=300)  # cache for 5 minutes
                final_queryset = final_queryset | qs

        return final_queryset

    def perform_create(self, serializer):
        instance = serializer.save(
            created_by=self.request.user, updated_by=self.request.user
        )
        # Invalidate cache for this instance's org
        cache.delete(f"scenerio_qs_org_{instance.organization_id}")

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        # Invalidate cache for updated org
        cache.delete(f"scenerio_qs_org_{instance.organization_id}")

    def perform_destroy(self, instance):
        org_id = instance.organization_id
        instance.delete()
        cache.delete(f"scenerio_qs_org_{org_id}")
