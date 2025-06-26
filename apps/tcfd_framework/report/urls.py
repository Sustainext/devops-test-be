from django.urls import path
from apps.tcfd_framework.report.views import TCFDReportGetView, TCFDReportUpsertView

urlpatterns = [
    path(
        "get-tcfd-report-data/<int:report_id>/<str:screen_name>/",
        TCFDReportGetView.as_view(),
        name="get-tcfd-report-data",
    ),
    path(
        "upsert-tcfd-report/",
        TCFDReportUpsertView.as_view(),
        name="upsert-tcfd-report",
    ),
]
