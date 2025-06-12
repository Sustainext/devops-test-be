from django.urls import path

from apps.tcfd_framework.views.TCFDReportingInformationViews import (
    TCFDReportingInformationView,
    TCFDReportingInformationCompletionView,
)

urlpatterns = [
    # * GET or PUT API for TCFD Reporting Information
    path(
        "tcfd-reporting-information/",
        TCFDReportingInformationView.as_view(),
        name="tcfd_reporting_information",
    ),
    # * Checks whether the TCFD Reporting Information is completed or not
    path(
        "tcfd-reporting-information-completion/",
        TCFDReportingInformationCompletionView.as_view(),
        name="tcfd_reporting_information_completion",
    ),
]
