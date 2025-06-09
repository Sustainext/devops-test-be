from django.urls import path
from apps.canada_bill_s211.v2.Views.ReportingForEntitiesView import (
    ReportingForEntitiesView,
)
from apps.canada_bill_s211.v2.Views.SubmissionInformationView import (
    SubmissionInformationView,
)
from apps.canada_bill_s211.v2.Views.StatusReport import StatusReport
from apps.canada_bill_s211.v2.Views.GetExcelReport import GetExcelReport
from apps.canada_bill_s211.v2.Views.GetReportData import GetReportData
from apps.canada_bill_s211.v2.Views.CreateReportData import CreateOrEditReportData
from apps.canada_bill_s211.v2.Views.GetCanadaReportPdf import GetCanadaReportPdf

urlpatterns = [
    path(
        "reporting-for-entities/<int:screen_id>/",
        ReportingForEntitiesView.as_view(),
        name="reporting-for-entities",
    ),
    path(
        "submission-information/<int:screen_id>/",
        SubmissionInformationView.as_view(),
        name="submission-information",
    ),
    path("status-report/", StatusReport.as_view(), name="status-report"),
    path("get-report/", GetExcelReport.as_view(), name="get-report"),
    path("get-report-data/", GetReportData.as_view(), name="get-report-data"),
    path(
        "create-report-data/",
        CreateOrEditReportData.as_view(),
        name="create-report-data",
    ),
    path(
        "get-report-pdf/<int:report_id>/",
        GetCanadaReportPdf.as_view(),
        name="get-report-pdf",
    ),
]
