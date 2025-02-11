from django_filters import rest_framework as filters
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeholderFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    email = filters.CharFilter(lookup_expr="icontains")
    country = filters.CharFilter(lookup_expr="icontains")
    city = filters.CharFilter(lookup_expr="icontains")
    state = filters.CharFilter(lookup_expr="icontains")
    updated_at = filters.DateTimeFilter()
    updated_at_after = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_at_before = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    class Meta:
        model = StakeHolder
        fields = [
            "name",
            "email",
            "updated_at",
            "updated_at_after",
            "updated_at_before",
            "country",
            "city",
            "state",
        ]
