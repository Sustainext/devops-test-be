from django.urls import path, include
from sustainapp.Views.SubCategoriesAPIView import SubCategoriesAPIView
from sustainapp.Views.ScopeCategoriesAPIView import ScopeCategoriesAPIView
from sustainapp.Views.ReportWordDownloadAPI import ReportWordDownloadAPI
from sustainapp.Views.ClientTaskView import UserClientViewset
from sustainapp.Views.OrganisationTaskList import UserTaskDashboardView
from sustainapp.Views.ZohoInfoModelViewset import ZohoInfoViewset
from sustainapp.Views.GetLocation import LocationListAPIView
from sustainapp.Views.EmissionAnalyse import GetEmissionAnalysis
from sustainapp.Views.EnergyAnalyse import EnergyAnalyzeView
from sustainapp.Views.EmissionTask import EmissionTask
from sustainapp.Views.AssignedEmissionTask import AssignedEmissionTask
from sustainapp.Views.Analyse.Social.EmploymentAnalyze import EmploymentAnalyzeView
from sustainapp.Views.Analyse.Economic.CommunicationTraining import (
    CommunicationTrainingAnalyzeView,
)
from sustainapp.Views.Analyse.Economic.OperationsAssesedAnalyse import (
    OperationsAssessedAnalyzeView,
)
from sustainapp.Views.Analyse.Governance.GovernanceAnalyse import GovernanceAnalyse
from rest_framework import routers
from sustainapp.Views.GHGReport import (
    GHGReportView,
    AnalysisData2APIView,
    ReportViewSet,
    ReportListView,
    ReportPDFView,
)
from sustainapp.Views.GetLocationAsPerCorporate import (
    GetLocationAsPerCorporate,
    GetLocationAsPerOrgOrCorp,
)
from sustainapp.Views.MaterialAnalyse import GetMaterialAnalysis
from sustainapp.Views.WasteAnalyse import GetWasteAnalysis
from sustainapp.Views.Analyse.Environment.WaterAnalyseAPI import (
    WaterAnalyseByDataPoints,
)
from sustainapp.Views.Analyse.Social.ForcedLaborAnalyze import ForcedLaborAnalyzeView
from sustainapp.Views.Analyse.Social.ChildLaborAndForcedLabour import (
    ChildLabourAndForcedLabourAnalyzeView,
)
from sustainapp.Views.Analyse.Social.GetOHSAnalyze import (
    OHSAnalysisView,
    GetIllnessAnalysisView,
)
from sustainapp.Views.Analyse.Social.DiversityAndInclusionAnalyse import (
    DiversityAndInclusionAnalyse,
)

from sustainapp.Views.Analyse.Social.SupplierSocialAssessment import (
    SupplierSocialAssessmentView,
)
from sustainapp.Views.Analyse.Social.NonDiscrimationAnalysis import (
    SocialNonDiscrimationAnalysis,
)
from sustainapp.Views.Analyse.Social.CollectiveBargainingAnalysis import (
    SocialCollectiveBargainingAnalysis,
)
from sustainapp.Views.Analyse.Social.SocialHumanRightsAndCommunityImpactAnalysis import (
    SocialHumanRightsAndCommunityImpactAnalysis,
)
from sustainapp.Views.Analyse.Social.CustomerPrivacyAnalyze import (
    CustomerPrivacyAnalyzeView,
)
from sustainapp.Views.Analyse.Social.CustomerHealthAnalyze import (
    CustomerHealthAnalyzeView,
)
from sustainapp.Views.Analyse.Social.MarketingLabelingAnalyze import (
    MarketingLabelingAnalyzeView,
)
from sustainapp.Views.GetAllCorporates import AllCorporateList
from sustainapp.Views.Analyse.General.GeneralEmployeeAnalyze import (
    GeneralEmployeeAnalyzeView,
)
from sustainapp.Views.Analyse.General.CollectiveBargainingAnalyze import (
    CollectiveBargainingAnalyzeView,
)
from sustainapp.Views.TrackDashboardView import TrackDashboardAPIView
from sustainapp.Views.Analyse.SupplierEnvironment.SupplierEnvironment import (
    SupplierEnvAnlayzeView,
)
from sustainapp.Views.OrgCorpLocViewset import CorporateListView, LocationListView
from sustainapp.Views.DepartmentViewset import DepartmentViewSet
from sustainapp.Views.ClimatiqCalling import ClimatiqDataAPIView
from sustainapp.Views.Analyse.Social.TrainingAnalyzeAPI import (
    TrainingAnalyzeAPI,
)
from sustainapp.Views.GetOrgLogs import AzureMonitorQueryView
from sustainapp.Views.PostOrgLogs import LogUploadView
from sustainapp.Views.MygoalOrganizationView import MyGoalOrganizationView

router = routers.DefaultRouter()
router.register("zoho_info", ZohoInfoViewset, basename="ZohoInfoViewset")
router.register(r"ghgreport", ReportViewSet, basename="ReportUpdate")
router.register(r"department", DepartmentViewSet, basename="Department")
router.register(r"my_goal", MyGoalOrganizationView, basename="MyGoalOrganization")

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
    path("get_approved_task/", EmissionTask.as_view(), name="emission_task"),
    path(
        "get_assigned_by_task/",
        AssignedEmissionTask.as_view(),
        name="assigned_emission_task",
    ),
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
        "get_location_as_per_org_or_corp/",
        GetLocationAsPerOrgOrCorp.as_view(),
        name="get_location_as_per_org_or_corp",
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
        "get_water_analysis_api/",
        WaterAnalyseByDataPoints.as_view(),
        name="get_water_analysis_api",
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
        "get_child_labor_and_forced_labour_analysis/",
        ChildLabourAndForcedLabourAnalyzeView.as_view(),
        name="get_child_labor_analysis",
    ),
    path(
        "get_ohs_analysis/",
        OHSAnalysisView.as_view(),
        name="get_ohs_analysis",
    ),
    path(
        "get_illness_analysis/",
        GetIllnessAnalysisView.as_view(),
        name="get_illness_analysis",
    ),
    path(
        "get_diversity_inclusion_analyse/",
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
        TrainingAnalyzeAPI.as_view(),
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
        "get_human_rights_and_community_impact_analysis/",
        SocialHumanRightsAndCommunityImpactAnalysis.as_view(),
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
    path(
        "get_marketing_and_labeling_analysis/",
        MarketingLabelingAnalyzeView.as_view(),
        name="get_marketing_and_labeling_analysis",
    ),
    path("all_corporate_list/", AllCorporateList.as_view(), name="all_corporate_list"),
    path(
        "get_governance_analysis/",
        GovernanceAnalyse.as_view(),
        name="get_governance_analysis",
    ),
    path(
        "get_general_employee_analysis/",
        GeneralEmployeeAnalyzeView.as_view(),
        name="get_general_employee_analysis",
    ),
    path(
        "get_general_collective_bargaining_analysis/",
        CollectiveBargainingAnalyzeView.as_view(),
        name="get_general_collective_bargaining_analysis",
    ),
    path("track_dashboards/", TrackDashboardAPIView.as_view(), name="track_dashboards"),
    path(
        "get_economic_operations_assessed/",
        OperationsAssessedAnalyzeView.as_view(),
        name="get_economic_operations_assessed",
    ),
    path(
        "get_economic_communication_and_training/",
        CommunicationTrainingAnalyzeView.as_view(),
        name="get_economic_communication_and_training",
    ),
    path(
        "get_analyze_supplier_assesment/",
        SupplierEnvAnlayzeView.as_view(),
        name="get_analyze_supplier_assesment",
    ),
    path("roles/corporates/", CorporateListView.as_view(), name="corporates-list"),
    path("roles/locations/", LocationListView.as_view(), name="locations-list"),
    path(
        "get_climatiq_data/",
        ClimatiqDataAPIView.as_view(),
        name="get_climatiq_data",
    ),
    path("get_org_logs/", AzureMonitorQueryView.as_view(), name="get_org_logs"),
    path("post_logs/", LogUploadView.as_view(), name="post-org-logs"),
]
