from django.urls import path
from materiality_dashboard.Views.GetSelectedFramework import GetSelectedFramework
from rest_framework.routers import DefaultRouter
from materiality_dashboard.Views.MaterialityAssesmentModelViewset import (
    MaterialityAssessmentViewSet,
)
from materiality_dashboard.Views.ListESGTopics import ListESGTopics
from materiality_dashboard.Views.AssessmentTopicSelectionViewset import (
    AssessmentTopicSelectionAPIView,
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
]
urlpatterns += router.urls
