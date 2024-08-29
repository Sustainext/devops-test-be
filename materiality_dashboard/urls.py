from django.urls import path
from materiality_dashboard.Views.GetSelectedFramework import GetSelectedFramework

urlpatterns = [
    path(
        "get_selected_framework/",
        GetSelectedFramework.as_view(),
        name="get-selected-framework",
    ),
]
