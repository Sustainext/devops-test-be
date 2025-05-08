from django.urls import path
from apps.canada_bill_s211.v2.Views.ReportingForEntitiesView import ReportingForEntitiesView
from apps.canada_bill_s211.v2.Views.SubmissionInformationView import SubmissionInformationView

urlpatterns = [
    path('reporting-for-entities/<int:screen_id>/', ReportingForEntitiesView.as_view(), name='reporting-for-entities'),
    path('submission-information/<int:screen_id>/', SubmissionInformationView.as_view(), name='submission-information'),
]
