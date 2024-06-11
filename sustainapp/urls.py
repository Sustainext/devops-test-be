from django.urls import path, include
from sustainapp.Views.SubCategoriesAPIView import SubCategoriesAPIView
from sustainapp.Views.ScopeCategoriesAPIView import ScopeCategoriesAPIView
from sustainapp.Views.ReportWordDownloadAPI import ReportWordDownloadAPI
from sustainapp.Views.OrganisationTaskList import OrganisationTaskDashboardView
from sustainapp.Views.ClientTaskView import UserClientViewset
from sustainapp.Views.OrganisationTaskList import UserTaskDashboardView
from sustainapp.Views.ChangePassword import ChangePasswordAPIView
from sustainapp.Views.ZohoInfoModelViewset import ZohoInfoViewset
from sustainapp.Views.GetLocation import LocationListAPIView
from sustainapp.Views.EmissionAnalyse import GetEmissionAnalysis
from rest_framework import routers
from sustainapp.Views.GHGReport import ReportCreateView

router = routers.DefaultRouter()
router.register("zoho_info", ZohoInfoViewset, basename="ZohoInfoViewset")
urlpatterns = [
    path("subcategories/", SubCategoriesAPIView.as_view(), name="subcategories"),
    path(
        "scope_categories/", ScopeCategoriesAPIView.as_view(), name="scope_categories"
    ),
    path(
        "report_word_download/<int:pk>/",
        ReportWordDownloadAPI.as_view(),
        name="report_word_download",
    ),
    path("user_client/", UserClientViewset.as_view(), name="user_client"),
    path("user_all_task/", UserTaskDashboardView.as_view(), name="user_all_task"),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("get_location/", LocationListAPIView.as_view(), name="get_location"),
    path("ghgreport/", ReportCreateView.as_view(), name="ghgreport"),
    path(
        "get_emission_analysis/",
        GetEmissionAnalysis.as_view(),
        name="get_emission_analysis",
    ),
    path("", include(router.urls)),
]
