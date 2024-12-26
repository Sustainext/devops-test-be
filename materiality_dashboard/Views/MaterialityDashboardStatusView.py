from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import (
    MaterialityAssessment,
    AssessmentTopicSelection,
    AssessmentDisclosureSelection,
    MaterialityChangeConfirmation,
    MaterialityAssessmentProcess,
    MaterialityImpact,
    ManagementApproachQuestion,
)
from django.db.models import Q


class MaterialityDashboardStatusView(APIView):
    """
    Provides an API view to retrieve the status of the materiality dashboard.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, materiality_id: int, format=None):
        """
        Retrieves the status of the materiality dashboard.
        """
        # ? How to add user based organisation and corporate in the filter?
        try:
            materiality_dashboard = MaterialityAssessment.objects.get(
                id=materiality_id,
                client=self.request.user.client,
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {"error": "Materiality assessment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        condition_for_completion = (
            AssessmentTopicSelection.objects.filter(
                assessment=materiality_dashboard
            ).exists()
            and AssessmentDisclosureSelection.objects.filter(
                topic_selection__assessment=materiality_dashboard
            ).exists()
            and MaterialityChangeConfirmation.objects.filter(
                assessment=materiality_dashboard
            ).exists()
            # * If in MaterialityAssessmentProcess field selected_stakeholders is empty and stakeholder_others is also empty then it will not be considered as completed
            and MaterialityAssessmentProcess.objects.filter(
                assessment=materiality_dashboard,
            )
            .filter(
                Q(selected_stakeholders__isnull=False, stakeholder_others="")
                | ~Q(stakeholder_others="", selected_stakeholders__isnull=True)
            )
            .filter(process_description__isnull=False)
            .filter(impact_assessment_process__isnull=False)
            .exists()
            and MaterialityImpact.objects.filter(
                assessment=materiality_dashboard
            ).exists()
            and ManagementApproachQuestion.objects.filter(
                assessment=materiality_dashboard,
                negative_impact_involvement_description__isnull=False,
                stakeholder_engagement_effectiveness_description__isnull=False,
            ).exists()
        )
        return Response(
            {"status": "completed" if condition_for_completion else "in_progress"}
        )
