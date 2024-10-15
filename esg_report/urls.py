from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ScreenOne import ScreenOneView
from esg_report.Views.ScreenTwo import ScreenTwo
from esg_report.Views.ScreenThree import ScreenThreeView
from esg_report.Views.ScreenFour import ScreenFourAPIView
from esg_report.Views.ScreenFive import ScreenFiveAPIView
from esg_report.Views.ScreenSix import ScreenSixAPIView
from esg_report.Views.ScreenSeven import ScreenSevenAPIView
from esg_report.Views.ScreenEight import ScreenEightAPIView
from esg_report.Views.ScreenNine import ScreenNineView
from esg_report.Views.ScreenTen import ScreenTenAPIView
from esg_report.Views.ScreenEleven import ScreenElevenAPIView
from esg_report.Views.ScreenTwelve import ScreenTwelveAPIView
from esg_report.Views.ScreenThirteen import ScreenThirteenView

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
    path(
        "screen_seven/<int:report_id>/",
        ScreenSevenAPIView.as_view(),
        name="screen_seven",
    ),
    path(
        "screen_eight/<int:report_id>/",
        ScreenEightAPIView.as_view(),
        name="screen_eight",
    ),
    path("screen_nine/<int:report_id>/", ScreenNineView.as_view(), name="screen_nine"),
    path(
        "screen_ten/<int:report_id>/",
        ScreenTenAPIView.as_view(),
        name="screen_ten",
    ),
    path(
        "screen_eleven/<int:report_id>/",
        ScreenElevenAPIView.as_view(),
        name="screen_eleven",
    ),
    path(
        "screen_twelve/<int:report_id>/",
        ScreenTwelveAPIView.as_view(),
        name="screen_twelve",
    ),
    path(
        "screen_thirteen/<int:report_id>/",
        ScreenThirteenView.as_view(),
        name="screen_thirteen",
    ),
]
urlpatterns += router.urls
