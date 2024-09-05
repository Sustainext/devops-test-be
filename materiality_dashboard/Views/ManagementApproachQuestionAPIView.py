from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import (
    ManagementApproachQuestion,
    MaterialityAssessment,
)
from materiality_dashboard.Serializers.ManagementApproachQuestionSerializer import (
    ManagementApproachQuestionSerializer,
)
from rest_framework.permissions import IsAuthenticated


class ManagementApproachQuestionCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ManagementApproachQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if ManagementApproachQuestion.objects.filter(
            assessment=serializer.validated_data["assessment"]
        ).exists():
            return Response(
                {
                    "error": "A Management Approach Question already exists for this assessment."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ManagementApproachQuestionEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, assessment_id):
        try:
            return ManagementApproachQuestion.objects.get(
                assessment__id=assessment_id,
                assessment__client__id=self.request.user.client.id,
            )
        except ManagementApproachQuestion.DoesNotExist:
            return None

    def put(self, request, assessment_id, *args, **kwargs):
        management_approach_question = self.get_object(assessment_id)
        if management_approach_question is None:
            return Response(
                {"error": "Management Approach Question not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ManagementApproachQuestionSerializer(
            management_approach_question, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagementApproachQuestionRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, assessment_id):
        try:
            return ManagementApproachQuestion.objects.get(
                assessment__id=assessment_id,
                assessment__client__id=self.request.user.client.id,
            )
        except ManagementApproachQuestion.DoesNotExist:
            return None

    def get(self, request, assessment_id, *args, **kwargs):
        management_approach_question = self.get_object(assessment_id)
        if management_approach_question is None:
            return Response(
                {"error": "Management Approach Question not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ManagementApproachQuestionSerializer(management_approach_question)
        return Response(serializer.data, status=status.HTTP_200_OK)
