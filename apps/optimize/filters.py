import django_filters
from .models.OptimizeScenario import Scenerio


class ScenarioFilter(django_filters.FilterSet):
    """This class defines the filter criteria for the Scenerio model.
    It allows filtering by name, base_year, corporate, organization, and target_year.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    corporate_name = django_filters.CharFilter(
        field_name="corporate__name", lookup_expr="icontains"
    )
    organization_name = django_filters.CharFilter(
        field_name="organization__name", lookup_expr="icontains"
    )
    base_year = django_filters.BaseInFilter(field_name="base_year", lookup_expr="in")
    target_year = django_filters.BaseInFilter(
        field_name="target_year", lookup_expr="in"
    )

    class Meta:
        model = Scenerio
        fields = [
            "name",
            "base_year",
            "target_year",
            "corporate_name",
            "organization_name",
        ]
