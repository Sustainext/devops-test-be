from rest_framework.views import APIView
from materiality_dashboard.models import AssessmentTopicSelection
from materiality_dashboard.Serializers.AssessmentTopicSelectionSerializer import (
    AssessmentTopicSelectionSerializer,
)
from materiality_dashboard.Serializers.MaterialTopicSerializer import (
    MaterialTopicModelSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from materiality_dashboard.models import MaterialityAssessment, MaterialTopic
from collections import defaultdict


class AssessmentTopicSelectionAPIView(APIView):
    """
    Topic Selection for Assessment
    Provides an API view for creating `AssessmentTopicSelection` objects.

    This view allows authenticated users to create one or more `AssessmentTopicSelection`
    objects, which represent the topics selected for a particular assessment.

    The view expects a list of topic IDs in the request data, and returns a list of
    the created `AssessmentTopicSelection` objects, including their IDs, the assessment
    ID, and the topic name.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AssessmentTopicSelectionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if AssessmentTopicSelection.objects.filter(
            assessment__id=serializer.validated_data["assessment_id"]
        ).exists():
            return Response(
                {"error": "Assessment topic selection already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        created_selections = AssessmentTopicSelection.objects.filter(
            assessment__id=serializer.validated_data["assessment_id"]
        ).select_related("topic")
        response_data = defaultdict(list)

        for selection in created_selections:
            response_data[selection.topic.esg_category].append(
                {
                    "id": selection.id,
                    "assessment_id": selection.assessment.id,
                    "topic_name": selection.topic.name,
                }
            )
        return Response(response_data, status=status.HTTP_201_CREATED)


class MaterialTopicsGETAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id, *args, **kwargs):
        # Retrieve the assessment object
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=self.request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {"error": "Materiality Assessment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all selected topics for this assessment
        topic_selections = AssessmentTopicSelection.objects.filter(
            assessment=assessment
        )
        material_topics = MaterialTopic.objects.filter(
            id__in=topic_selections.values_list("topic_id", flat=True)
        )

        # Filter by esg_category if provided
        esg_category = request.query_params.get("esg_category")
        if esg_category:
            material_topics = material_topics.filter(esg_category=esg_category)

        # Serialize and return the data
        serializer = MaterialTopicModelSerializer(material_topics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssessmentTopicSelectionUpdateAPIView(APIView):
    """
    Update API for Assessment Topic Selection
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, assessment_id, *args, **kwargs):
        # Retrieve the assessment instance
        try:
            assessment = MaterialityAssessment.objects.get(
                id=assessment_id, client=self.request.user.client
            )
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {"error": "Materiality Assessment does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate that the payload contains "topics"
        topics = request.data.get("topics", [])
        if not isinstance(topics, list):
            return Response(
                {"error": "Expected 'topics' to be a list of topic IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert the topics from the request to integers to match the database type
        new_topic_ids = set(map(int, topics))

        # Get the existing topic selections for this assessment and convert them to a set
        existing_selections = AssessmentTopicSelection.objects.filter(assessment=assessment)
        existing_topic_ids = set(existing_selections.values_list('topic_id', flat=True))

        # Topics to add (present in the new list but not in the existing ones)
        topics_to_add = new_topic_ids - existing_topic_ids

        # Topics to remove (present in the existing list but not in the new ones)
        topics_to_remove = existing_topic_ids - new_topic_ids

        # Remove the selections that are no longer in the updated list
        if topics_to_remove:
            AssessmentTopicSelection.objects.filter(
                assessment=assessment, topic_id__in=topics_to_remove
            ).delete()

        # Add new selections for the topics that were added
        for topic_id in topics_to_add:
            AssessmentTopicSelection.objects.create(
                assessment=assessment,
                topic_id=topic_id
            )

        # Query the updated selections (including newly created ones)
        updated_selections = AssessmentTopicSelection.objects.filter(
            assessment=assessment
        ).select_related("topic")

        # Prepare the response data
        response_data = [
            {
                "id": selection.id,
                "topic_id": selection.topic.id,
                "assessment_id": selection.assessment.id,
                "topic_name": selection.topic.name,
                "esg_category": selection.topic.esg_category,
            }
            for selection in updated_selections
        ]

        return Response(response_data, status=status.HTTP_200_OK)