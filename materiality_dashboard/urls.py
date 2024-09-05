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
    AssessmentTopicSelectionUpdateAPIView,
)
from materiality_dashboard.Views.AssessmentDisclosureSelectionViewset import (
    AssessmentDisclosureSelectionCreate,
    AssessmentDisclosureSelectionRetrieve,
    AssessmentDisclosureSelectionUpdate,
    GetMaterialTopicDisclosures,
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

router = DefaultRouter()
router.register(
    r"materiality-assessments",
    MaterialityAssessmentViewSet,
    basename="materiality-assessment",
)


urlpatterns = [
    # * Get all materiality assessments for a particular client
    path(
        "get-materiality-assessments-dashboard/",
        MaterialityAssessmentListAPIView.as_view(),
        name="materiality-assessment-list",
    ),
    # * Get Selected Frameworks of all the organisations associated with the user.
    path(
        "get_selected_framework/",
        GetSelectedFramework.as_view(),
        name="get-selected-framework",
    ),
    # * Get all the material topics for a particular framework.
    path("list-esg-topics/", ListESGTopics.as_view(), name="list-esg-topics"),
    # * Select the material topics for a particular materiality assessment.
    path(
        "assessment-topic-selection/",
        AssessmentTopicSelectionAPIView.as_view(),
        name="assessment-topic-selection",
    ),
    # * To Edit the material topic selection of a particular materiality assessment.
    path(
        "assessment-topic-selections/<int:assessment_id>/edit/",
        AssessmentTopicSelectionUpdateAPIView.as_view(),
        name="assessment-topic-selection-edit",
    ),
    # * To get selected material topics of the materiality assessment.
    path(
        "get-material-topics/<int:assessment_id>/",
        MaterialTopicsGETAPIView.as_view(),
        name="get-material-topics",
    ),
    # * To get all material topic disclosures of the topics selected in a particular Materiality Assessment.
    path(
        "get-material-topic-disclosures/<int:assessment_id>/",
        GetMaterialTopicDisclosures.as_view(),
    ),
    # * To Select Disclosures for the selected material topics of a particular materiality assessment.
    path(
        "assessment-disclosure-selection/",
        AssessmentDisclosureSelectionCreate.as_view(),
        name="assessment-disclosure-selection",
    ),
    # * To get all the disclosures of the selected material topics of a particular materiality assessment.
    path(
        "assessment-disclosure-selection/<int:assessment_id>/",
        AssessmentDisclosureSelectionRetrieve.as_view(),
        name="bulk-assessment-disclosure-selection-list",
    ),
    # * To update disclosures for the selected material topics of a particular materiality assessment.
    path(
        "assessment-disclosure-selection/<int:assessment_id>/edit/",
        AssessmentDisclosureSelectionUpdate.as_view(),
        name="bulk-assessment-disclosure-selection-edit",
    ),
    # * To Store data related to Materiality Change Confirmation Screen
    path(
        "materiality-change-confirmation/create/",
        MaterialityChangeConfirmationCreateAPIView.as_view(),
        name="materiality-change-confirmation-create",
    ),
    # * To get data related to Materiality Change Confirmation Screen
    path(
        "materiality-change-confirmation/<int:assessment_id>/",
        MaterialityChangeConfirmationDetailAPIView.as_view(),
        name="materiality-change-confirmation-detail",
    ),
    # * To get all the stakeholders for many to many relationship
    path(
        "stakeholder-engagements/",
        StakeholderEngagementListAPIView.as_view(),
        name="stakeholder-engagement-list",
    ),
    # * To get all the selected material topic IDs for a particular materiality assessment.
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
