import django_filters
from .models.OptimizeScenario import Scenerio


class ScenarioFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    base_year = django_filters.BaseInFilter(field_name="base_year", lookup_expr="in")
    corporate = django_filters.BaseInFilter(field_name="corporate", lookup_expr="in")
    organization = django_filters.BaseInFilter(
        field_name="organization", lookup_expr="in"
    )
    target_year = django_filters.BaseInFilter(
        field_name="target_year", lookup_expr="in"
    )

    class Meta:
        model = Scenerio
        fields = ["name", "base_year", "target_year", "corporate", "organization"]
