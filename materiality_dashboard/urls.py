from django.urls import path
from materiality_dashboard.Views.GetSelectedFramework import GetSelectedFramework
from rest_framework.routers import DefaultRouter
from materiality_dashboard.Views.MaterialityAssesmentModelViewset import (
    MaterialityAssessmentViewSet,
)
from materiality_dashboard.Views.ListESGTopics import ListESGTopics
from materiality_dashboard.Views.AssessmentTopicSelectionViewset import (
    AssessmentTopicSelectionAPIView,
    MaterialTopicsGETAPIView,
)
from materiality_dashboard.Views.AssessmentDisclosureSelectionViewset import (
    AssessmentDisclosureSelectionAPIView,
)
from materiality_dashboard.Views.MaterialityAssessmentDashboardGetAPI import (
    MaterialityAssessmentListAPIView,
)
from materiality_dashboard.Views.MaterialityAssessmentChange import (
    MaterialityChangeConfirmationCreateAPIView,
    MaterialityChangeConfirmationDetailAPIView,
)
from materiality_dashboard.Views.StakeholderEngagementListAPIView import (
    StakeholderEngagementListAPIView,
)
from materiality_dashboard.Views.SelectedMaterialTopicsAPIView import (
    SelectedMaterialTopicsAPIView,
)
from materiality_dashboard.Views.MaterialityImpactAPIView import (
    MaterialityImpactCreateAPIView,
    MaterialityImpactEditAPIView,
    MaterialityImpactListAPIView,
)
from materiality_dashboard.Views.ManagementApproachQuestionAPIView import (
    ManagementApproachQuestionCreateAPIView,
    ManagementApproachQuestionEditAPIView,
    ManagementApproachQuestionRetrieveAPIView,
)
from materiality_dashboard.Views.MaterialityAssessmentProcessAPIViews import (
    MaterialityAssessmentProcessCreateAPIView,
    MaterialityAssessmentProcessDetailAPIView,
)
from materiality_dashboard.Views.AssessmentDisclosureSelectionViewset import (
    GetMaterialTopicDisclosures,
)

router = DefaultRouter()
router.register(
    r"materiality-assessments",
    MaterialityAssessmentViewSet,
    basename="materiality-assessment",
)


urlpatterns = [
    path(
        "get_selected_framework/",
        GetSelectedFramework.as_view(),
        name="get-selected-framework",
    ),
    path("list-esg-topics/", ListESGTopics.as_view(), name="list-esg-topics"),
    path(
        "assessment-topic-selection/",
        AssessmentTopicSelectionAPIView.as_view(),
        name="assessment-topic-selection",
    ),
    path(
        "assessment-topic-selections/<int:assessment_id>/edit/",
        AssessmentTopicSelectionAPIView.as_view(),
        name="assessment-topic-selection-edit",
    ),
    path(
        "get-material-topics/<int:assessment_id>/",
        MaterialTopicsGETAPIView.as_view(),
        name="get-material-topics",
    ),
    path(
        "get-material-topic-disclosures/<int:assessment_id>/",
        GetMaterialTopicDisclosures.as_view(),
    ),
    path(
        "assessment-disclosure-selection/",
        AssessmentDisclosureSelectionAPIView.as_view(),
        name="assessment-disclosure-selection",
    ),
    path(
        "assessment-disclosure-selection/<int:assessment_id>/",
        AssessmentDisclosureSelectionAPIView.as_view(),
        name="bulk-assessment-disclosure-selection-list",
    ),
    path(
        "assessment-disclosure-selection/<int:assessment_id>/edit/",
        AssessmentDisclosureSelectionAPIView.as_view(),
        name="bulk-assessment-disclosure-selection-edit",
    ),
    path(
        "get-materiality-assessments-dashboard/",
        MaterialityAssessmentListAPIView.as_view(),
        name="materiality-assessment-list",
    ),
    path(
        "materiality-change-confirmation/create/",
        MaterialityChangeConfirmationCreateAPIView.as_view(),
        name="materiality-change-confirmation-create",
    ),
    path(
        "materiality-change-confirmation/<int:assessment_id>/",
        MaterialityChangeConfirmationDetailAPIView.as_view(),
        name="materiality-change-confirmation-detail",
    ),
    path(
        "stakeholder-engagements/",
        StakeholderEngagementListAPIView.as_view(),
        name="stakeholder-engagement-list",
    ),
    path(
        "selected-material-topics/<int:assessment_id>/",
        SelectedMaterialTopicsAPIView.as_view(),
        name="selected-material-topics",
    ),
    path(
        "materiality-impact/create/",
        MaterialityImpactCreateAPIView.as_view(),
        name="materiality-impact-create",
    ),
    path(
        "materiality-impact/<int:assessment_id>/",
        MaterialityImpactListAPIView.as_view(),
        name="materiality-impact-list",
    ),
    path(
        "materiality-impact/<int:assessment_id>/<int:pk>/",
        MaterialityImpactEditAPIView.as_view(),
        name="materiality-impact-edit",
    ),
    path(
        "management-approach-question/create/",
        ManagementApproachQuestionCreateAPIView.as_view(),
        name="management-approach-question-create",
    ),
    path(
        "management-approach-question/<int:assessment_id>/edit/",
        ManagementApproachQuestionEditAPIView.as_view(),
        name="management-approach-question-edit",
    ),
    path(
        "management-approach-question/<int:assessment_id>/",
        ManagementApproachQuestionRetrieveAPIView.as_view(),
        name="management-approach-question-retrieve",
    ),
    path(
        "materiality-assessment-process/create/",
        MaterialityAssessmentProcessCreateAPIView.as_view(),
        name="materiality-assessment-process-create",
    ),
    path(
        "materiality-assessment-process/<int:assessment_id>/",
        MaterialityAssessmentProcessDetailAPIView.as_view(),
        name="materiality-assessment-process-detail",
    ),
]
urlpatterns += router.urls
