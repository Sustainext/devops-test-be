from django.urls import path
from apps.canada_bill_s211.v2.Views.ReportingForEntitiesView import ReportingForEntitiesView
from apps.canada_bill_s211.v2.Views.SubmissionInformationView import SubmissionInformationView
from apps.canada_bill_s211.v2.Views.StatusReport import StatusReport
from apps.canada_bill_s211.v2.Views.GetReport import GetReport
urlpatterns = [
    path('reporting-for-entities/<int:screen_id>/', ReportingForEntitiesView.as_view(), name='reporting-for-entities'),
    path('submission-information/<int:screen_id>/', SubmissionInformationView.as_view(), name='submission-information'),
    path('status-report/', StatusReport.as_view(), name='status-report'),
    path('get-report/', GetReport.as_view(), name='get-report'),
]
