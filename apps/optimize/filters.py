import django_filters
from apps.optimize.models.OptimizeScenario import Scenerio
from datametric.models import EmissionAnalysis
from django.db.models import Q
from apps.optimize.models.CalculatedResult import CalculatedResult


class ScenarioFilter(django_filters.FilterSet):
    """This class defines the filter criteria for the Scenerio model.
    It allows filtering by name, base_year, corporate, organization, and target_year.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    corporate = django_filters.BaseInFilter(field_name="corporate", lookup_expr="in")
    organization = django_filters.BaseInFilter(
        field_name="organization", lookup_expr="in"
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
            "corporate",
            "organization",
        ]


class EmissionDataFilter(django_filters.FilterSet):
    """This class defines the filter criteria for the EmissionAnalysis model.
    It allows filtering by category and subcategory.
    """

    scope = django_filters.CharFilter(method="filter_by_scope", lookup_expr="iexact")
    category = django_filters.CharFilter(
        method="filter_by_category", lookup_expr="iexact"
    )
    subcategory = django_filters.CharFilter(
        method="filter_by_subcategory", lookup_expr="iexact"
    )
    search = django_filters.CharFilter(method="filter_search")

    def filter_by_scope(self, queryset, name, value):
        scopes = value.split(",")
        return queryset.filter(scope__in=scopes)

    def filter_by_category(self, queryset, name, value):
        categories = value.split(",")
        return queryset.filter(category__in=categories)

    def filter_by_subcategory(self, queryset, name, value):
        subcategories = value.split(",")
        return queryset.filter(subcategory__in=subcategories)

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(scope__icontains=value)
            | Q(category__icontains=value)
            | Q(subcategory__icontains=value)
            | Q(activity__icontains=value)
        )

    class Meta:
        model = EmissionAnalysis
        fields = ["category", "subcategory"]


class CommaSeparatedListFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class CalculatedResultFilter(django_filters.FilterSet):
    scope = django_filters.CharFilter(method="filter_by_scope")
    category = django_filters.CharFilter(method="filter_by_category")
    sub_category = django_filters.CharFilter(method="filter_by_sub_category")
    activity_id = django_filters.CharFilter(method="filter_by_activity_id")
    activity_name = django_filters.CharFilter(method="filter_by_activity_name")
    metric = django_filters.CharFilter(method="filter_by_metric")

    def filter_by_scope(self, queryset, name, value):
        scopes = value.split(",")
        return queryset.filter(scope__in=scopes)

    def filter_by_category(self, queryset, name, value):
        categories = value.split(",")
        return queryset.filter(category__in=categories)

    def filter_by_sub_category(self, queryset, name, value):
        sub_categories = value.split(",")
        return queryset.filter(sub_category__in=sub_categories)

    def filter_by_activity_id(self, queryset, name, value):
        activity_ids = value.split(",")
        return queryset.filter(activity_id__in=activity_ids)

    def filter_by_activity_name(self, queryset, name, value):
        activity_names = value.split(",")
        return queryset.filter(activity_name__in=activity_names)

    def filter_by_metric(self, queryset, name, value):
        metrics = value.split(",")
        return queryset.filter(metric__in=metrics)

    class Meta:
        model = CalculatedResult
        fields = [
            "scope",
            "category",
            "sub_category",
            "activity_id",
            "activity_name",
            "metric",
        ]
