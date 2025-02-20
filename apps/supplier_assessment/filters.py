from django_filters import rest_framework as filters
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from apps.supplier_assessment.models.StakeHolderGroup import StakeHolderGroup


# Create a custom filter to handle multiple email values.
class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


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
    oldest_email = filters.CharFilter(
        field_name="oldest_email", lookup_expr="icontains"
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
            "oldest_email",
        ]


class StakeHolderGroupFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    group_type = filters.CharFilter(lookup_expr="icontains")
    organization__name = filters.CharFilter(lookup_expr="icontains")
    corporate_entity__name = filters.CharFilter(lookup_expr="icontains")
    created_by__username = filters.CharFilter(lookup_expr="icontains")
    created_by__username_exact = filters.CharFilter(
        field_name="created_by__username", lookup_expr="exact"
    )
    created_by__email = filters.CharFilter(lookup_expr="icontains")
    created_by__email_in = CharInFilter(
        field_name="created_by__email", lookup_expr="in"
    )

    created_at_after = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_before = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    created_by__first_name = filters.CharFilter(lookup_expr="icontains")
    created_by__last_name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = StakeHolderGroup
        fields = [
            "name",
            "group_type",
            "organization__name",
            "corporate_entity__name",
            "created_by__username",
            "created_by__username_exact",
            "created_at_after",
            "created_at_before",
            "created_by__email",
            "created_by__email_in",
            "created_by__first_name",
            "created_by__last_name",
        ]
