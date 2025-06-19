from django.urls import path, include

from apps.tcfd_framework.views.TCFDReportingInformationViews import (
    TCFDReportingInformationView,
)
from apps.tcfd_framework.views.TCFDCompletionStatus import (
    TCFDStatusCompletionView,
)
from apps.tcfd_framework.views.TCFDCollectViews import (
    GetTCFDDisclosures,
    UpdateSelectedDisclosures,
    GetLatestSelectedDisclosures,
)
from apps.tcfd_framework.views.CollectDataScreen import CollectDataScreen
from apps.tcfd_framework.views.TCFDReportPDF import GetTCFDReportPdf

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
        TCFDStatusCompletionView.as_view(),
        name="tcfd_reporting_information_completion",
    ),
    # * GET API for TCFD Collect Section Disclosures
    path(
        "tcfd-collect-disclosures/",
        GetTCFDDisclosures.as_view(),
        name="tcfd_collect_disclosures",
    ),
    # * GET or PUT API for Selected Disclosures
    path(
        "selected-disclosures/",
        UpdateSelectedDisclosures.as_view(),
        name="get_or_update_selected_disclosures",
    ),
    # * Get Latest Selected Disclosures API
    path(
        "get-latest-selected-disclosures/",
        GetLatestSelectedDisclosures.as_view(),
        name="get_or_update_selected_disclosures",
    ),
    # * Get data from different collect section
    path(
        "get-climate-related-data/",
        CollectDataScreen.as_view(),
        name="get-climate-related-data",
    ),
    path("report/", include("apps.tcfd_framework.report.urls")),
    # * Get TCFD Report PDF
    path(
        "get-tcfd-report-pdf/<int:report_id>/",
        GetTCFDReportPdf.as_view(),
        name="get-tcfd-report-pdf",
    ),
]
