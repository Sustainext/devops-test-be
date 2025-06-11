from django.urls import path

from apps.tcfd_framework.views.TCFDReportingInformationViews import (
    TCFDReportingInformationView,
    TCFDReportingInformationCompletionView,
)

urlpatterns = [
    path(
        "tcfd-reporting-information/",
        TCFDReportingInformationView.as_view(),
        name="tcfd_reporting_information",
    ),
    path(
        "tcfd-reporting-information-completion/",
        TCFDReportingInformationCompletionView.as_view(),
        name="tcfd_reporting_information_completion",
    ),
]
