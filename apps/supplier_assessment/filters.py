from django_filters import rest_framework as filters
from apps.supplier_assessment.models.StakeHolder import StakeHolder


class StakeholderFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    email = filters.CharFilter(lookup_expr="icontains")
    updated_at = filters.DateTimeFilter()

    class Meta:
        model = StakeHolder
        fields = ["name", "email", "updated_at"]
