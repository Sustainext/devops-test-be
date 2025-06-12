from django.urls import path

from apps.tcfd_framework.views.TCFDReportingInformationViews import (
    TCFDReportingInformationView,
    TCFDReportingInformationCompletionView,
)
from apps.tcfd_framework.views.TCFDCollectViews import (
    GetTCFDDisclosures,
    GetOrUpdateSelectedDisclosures,
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
    # * GET API for TCFD Collect Section Disclosures
    path(
        "tcfd-collect-disclosures/",
        GetTCFDDisclosures.as_view(),
        name="tcfd_collect_disclosures",
    ),
    # * GET or PUT API for Selected Disclosures
    path(
        "selected-disclosures/",
        GetOrUpdateSelectedDisclosures.as_view(),
        name="get_or_update_selected_disclosures",
    ),
]
