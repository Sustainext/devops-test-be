from django.urls import path, include
from sustainapp.Views.SubCategoriesAPIView import SubCategoriesAPIView
from sustainapp.Views.ScopeCategoriesAPIView import ScopeCategoriesAPIView
from sustainapp.Views.ReportWordDownloadAPI import ReportWordDownloadAPI
from sustainapp.Views.OrganisationTaskList import OrganisationTaskDashboardView
from sustainapp.Views.ClientTaskView import UserClientViewset
from sustainapp.Views.OrganisationTaskList import UserTaskDashboardView
from sustainapp.Views.ZohoInfoModelViewset import ZohoInfoViewset
from sustainapp.Views.GetLocation import LocationListAPIView
from sustainapp.Views.EmissionAnalyse import GetEmissionAnalysis
from sustainapp.Views.EnergyAnalyse import EnergyAnalyzeView
from sustainapp.Views.Analyse.Social.EmploymentAnalyze import EmploymentAnalyzeView
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
from sustainapp.Views.Analyse.WaterAnalyse import WaterAnalyse
from sustainapp.Views.Analyse.Social.ForcedLaborAnalyze import ForcedLaborAnalyzeView
from sustainapp.Views.Analyse.Social.ChildLabor import ChildLabourAnalyzeView
from sustainapp.Views.Analyse.Social.IllnessAnalyse import IllnessAnalysisView
from sustainapp.Views.Analyse.Social.DiversityAndInclusionAnalyse import (
    DiversityAndInclusionAnalyse,
)
from sustainapp.Views.Analyse.Social.SupplierSocialAssessment import (
    SupplierSocialAssessmentView,
)
from sustainapp.Views.Analyse.Social.TrainingAnalyse import TrainingSocial
from sustainapp.Views.Analyse.Social.NonDiscrimationAnalysis import (
    SocialNonDiscrimationAnalysis,
)
from sustainapp.Views.Analyse.Social.CollectiveBargainingAnalysis import (
    SocialCollectiveBargainingAnalysis,
)
from sustainapp.Views.Analyse.Social.CommunityDevelopmentAnalyse import (
    SocialCommunityDevelopmentAnalysis,
)
from sustainapp.Views.Analyse.Social.CustomerPrivacyAnalyze import (
    CustomerPrivacyAnalyzeView,
)
from sustainapp.Views.Analyse.Social.CustomerHealthAnalyze import (
    CustomerHealthAnalyzeView,
)


router = routers.DefaultRouter()
router.register("zoho_info", ZohoInfoViewset, basename="ZohoInfoViewset")
router.register(r"ghgreport", ReportViewSet, basename="ReportUpdate")
urlpatterns = [
    path("", include(router.urls)),
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
    path(
        "get_water_analysis/",
        WaterAnalyse.as_view(),
        name="get_water_analysis",
    ),
    path(
        "get_employment_analysis/",
        EmploymentAnalyzeView.as_view(),
        name="get_employment_analyze",
    ),
    path(
        "get_forced_labor_analysis/",
        ForcedLaborAnalyzeView.as_view(),
        name="get_forced_labor_analysis",
    ),
    path(
        "get_child_labor_analysis/",
        ChildLabourAnalyzeView.as_view(),
        name="get_child_labor_analysis",
    ),
    path(
        "get_ohs_analysis/",
        IllnessAnalysisView.as_view(),
        name="get_ohs_analysis",
    ),
    path(
        "get_diversity_inclusion_analysis/",
        DiversityAndInclusionAnalyse.as_view(),
        name="get_diversity_inclusion_analysis",
    ),
    path(
        "get_supplier_social_assessment_analysis/",
        SupplierSocialAssessmentView.as_view(),
        name="get_supplier_social_assessment_analysis",
    ),
    path(
        "get_training_social_analysis/",
        TrainingSocial.as_view(),
        name="get_training_social_analysis",
    ),
    path(
        "get_non_discrimination_analysis/",
        SocialNonDiscrimationAnalysis.as_view(),
        name="get_non_discrimination_analysis",
    ),
    path(
        "get_collective_bargaining_analysis/",
        SocialCollectiveBargainingAnalysis.as_view(),
        name="get_collective_bargaining_analysis",
    ),
    path(
        "get_community_development_analysis/",
        SocialCommunityDevelopmentAnalysis.as_view(),
        name="get_community_development_analysis",
    ),
    path(
        "get_customer_privacy_analysis/",
        CustomerPrivacyAnalyzeView.as_view(),
        name="get_customer_privacy_analysis",
    ),
    path(
        "get_customer_health_safety_analysis/",
        CustomerHealthAnalyzeView.as_view(),
        name="get_customer_health_safety_analysis",
    ),

]
