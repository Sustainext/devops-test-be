from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ScreenOne import ScreenOneView
from esg_report.Views.ScreenTwo import ScreenTwo
from esg_report.Views.ScreenThree import ScreenThreeView
from esg_report.Views.ScreenFour import ScreenFourAPIView
from esg_report.Views.ScreenFive import ScreenFiveAPIView
from esg_report.Views.ScreenSix import ScreenSixAPIView

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
    path(
        "screen_three/<int:report_id>/",
        ScreenThreeView.as_view(),
        name="screen_three",
    ),
    path(
        "screen_four/<int:report_id>/",
        ScreenFourAPIView.as_view(),
        name="screen_four",
    ),
    path(
        "screen_five/<int:report_id>/",
        ScreenFiveAPIView.as_view(),
        name="screen_five",
    ),
    path(
        "screen_six/<int:report_id>/",
        ScreenSixAPIView.as_view(),
        name="screen_six",
    ),
    
]
urlpatterns += router.urls
