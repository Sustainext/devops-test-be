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
from sustainapp.Views.EnergyAnalyse import EnergyAnalyzeView
from rest_framework import routers
from sustainapp.Views.GHGReport import (
    GHGReportView,
    AnalysisData2APIView,
    ReportViewSet,
    ReportListView,
    ReportPDFView,
)
from sustainapp.Views.GetLocationAsPerCorporate import GetLocationAsPerCorporate
from sustainapp.Views.MaterialAnalyse import GetMaterialAnalysis
from sustainapp.Views.WasteAnalyse import GetWasteAnalysis

router = routers.DefaultRouter()
router.register("zoho_info", ZohoInfoViewset, basename="ZohoInfoViewset")
router.register(r"ghgreport", ReportViewSet, basename="ReportUpdate")
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
    path(
        "get_emission_analysis/",
        GetEmissionAnalysis.as_view(),
        name="get_emission_analysis",
    ),
    path(
        "get_energy_analysis/",
        EnergyAnalyzeView.as_view(),
        name="get_energy_analysis",
    ),
    path(
        "report_data/<str:report_id>/",
        AnalysisData2APIView.as_view(),
        name="report_data",
    ),
    path("report_create/", GHGReportView.as_view(), name="report_create"),
    path("report_details/", ReportListView.as_view(), name="report_details"),
    path("report_pdf/<int:pk>/", ReportPDFView.as_view(), name="report_pdf"),
    path(
        "get_location_as_per_corporate/",
        GetLocationAsPerCorporate.as_view(),
        name="get_location_as_per_corporate",
    ),
    path(
        "get_material_analysis/",
        GetMaterialAnalysis.as_view(),
        name="get_material_analysis",
    ),
    path(
        "get_waste_analysis/",
        GetWasteAnalysis.as_view(),
        name="get_waste_analysis",
    ),
    path("", include(router.urls)),
]
