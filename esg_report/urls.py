from django.urls import path
from rest_framework.routers import DefaultRouter
from esg_report.Views.ESGReportViewset import (
    ESGReportIntroductionChoices,
    ESGReportIntroductionGETAPIView,
    ESGReportIntroductionPOSTAPIView,
    ESGReportIntroductionPUTAPIView,
)
from esg_report.Views.GetStakeholderEngagements import (
    GetApproachToStakeholderEngagementView,
    GetStakeholderEngagementView,
)
from esg_report.Views.GetAboutTheCompanyOperationsInfo import (
    GetAboutTheCompanyOperationsInfoView,
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
    path(
        "get_stakeholder_engagement/<int:report_id>/",
        GetStakeholderEngagementView.as_view(),
        name="get_stakeholder_engagement",
    ),
    path(
        "get_approach_to_stakeholder_engagement/<int:report_id>/",
        GetApproachToStakeholderEngagementView.as_view(),
        name="get_approach_to_stakeholder_engagement",
    ),
    path(
        "get_about_the_company_operations_info/<int:report_id>/",
        GetAboutTheCompanyOperationsInfoView.as_view(),
        name="get_about_the_company_operations_info",
    ),
    
]
urlpatterns += router.urls
