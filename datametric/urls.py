from django.urls import path
from .views import (
    TestView,
    FieldGroupListView,
    CreateOrUpdateFieldGroup,
    GetComputedClimatiqValue,
    UpdateFieldGroupView,
)
from datametric.View.UpdateOrCreateIndicator import UpdateOrCreateIndicatorView

urlpatterns = [
    path("test/", TestView.as_view(), name="udm-test"),
    path(
        "get-fieldgroups", FieldGroupListView.as_view(), name="get-fieldgroup-from-slug"
    ),
    path(
        "update-fieldgroup",
        CreateOrUpdateFieldGroup.as_view(),
        name="update-create-fieldgroup",
    ),
    path(
        "get-climatiq-score",
        GetComputedClimatiqValue.as_view(),
        name="get-computed-climatiq-view",
    ),
    path(
        "update-field-group-with-path/",
        UpdateFieldGroupView.as_view(),
        name="update-field-group",
    ),
    path(
        "update-or-create-indicator/",
        UpdateOrCreateIndicatorView.as_view(),
        name="update-or-create-indicator",
    ),
]
