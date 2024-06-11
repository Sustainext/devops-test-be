from django.urls import path
from .views import TestView, FieldGroupListView, CreateOrUpdateFieldGroup,GetComputedClimatiqValue

urlpatterns = [
    path("test/", TestView.as_view(), name="udm-test"),
    path("get-fieldgroups", FieldGroupListView.as_view(), name="get-fieldgroup-from-slug"),
    path("update-fieldgroup",CreateOrUpdateFieldGroup.as_view(),name="update-create-fieldgroup"),
    path('get-climatiq-score',GetComputedClimatiqValue.as_view(),name="get-computed-climatiq-view")
]
