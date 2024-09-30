from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ScreenOne import ScreenOneView
from esg_report.Views.ScreenTwo import ScreenTwo

router = DefaultRouter()

urlpatterns = [
    path(
        "screen_one/<int:esg_report_id>/",
        ScreenOneView.as_view(),
        name="screen_one",
    ),
    path(
        "screen_two/<int:report_id>/",
        ScreenTwo.as_view(),
        name="screen_two",
    ),
]
urlpatterns += router.urls
