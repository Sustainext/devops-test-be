from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ESGReportViewset import (
    ESGReportIntroductionChoices,
    ESGReportIntroductionGETAPIView,
    ESGReportIntroductionPOSTAPIView,
    ESGReportIntroductionPUTAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path(
        "esg_report_introduction_choices/",
        ESGReportIntroductionChoices.as_view(),
        name="esg_report_introduction_choices",
    ),
    path(
        "esg_report_introduction/<int:esg_report_id>/retrieve/",
        ESGReportIntroductionGETAPIView.as_view(),
        name="esg_report_introduction_get",
    ),
    path(
        "esg_report_introduction/create/",
        ESGReportIntroductionPOSTAPIView.as_view(),
        name="esg_report_introduction_post",
    ),
    path(
        "esg_report_introduction/<int:esg_report_id>/edit/",
        ESGReportIntroductionPUTAPIView.as_view(),
        name="esg_report_introduction_put",
    ),
]
urlpatterns += router.urls
