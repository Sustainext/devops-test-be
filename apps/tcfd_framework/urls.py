from django.urls import path

from apps.tcfd_framework.views.TCFDReportingInformationViews import (
    TCFDReportingInformationView,
)

urlpatterns = [
    path(
        "tcfd-reporting-information/",
        TCFDReportingInformationView.as_view(),
        name="tcfd_reporting_information",
    ),
]
