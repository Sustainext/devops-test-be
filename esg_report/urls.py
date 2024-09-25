from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ScreenOne import ScreenOneView


router = DefaultRouter()

urlpatterns = [
    path(
        "esg_report/<int:esg_report_id>/screen_one/",
        ScreenOneView.as_view(),
        name="screen_one",
    ),
]
urlpatterns += router.urls
