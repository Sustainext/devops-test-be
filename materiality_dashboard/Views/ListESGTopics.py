# * Create a GET API that shows all the ESG topics
from materiality_dashboard.models import MaterialTopic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.Serializers.MaterialTopicSerializer import (
    MaterialTopicModelSerializer,
    CustomFrameworkSerializer,
)


class ListESGTopics(APIView):
    """
    Provides an API endpoint to retrieve a list of all ESG topics associated with a specific framework.

    The `ListESGTopics` class is an `APIView` that requires authentication (`IsAuthenticated` permission). When a GET request is made to this endpoint, it will:

    1. Deserialize the `framework_id` parameter from the query string using the `CustomFrameworkSerializer`.
    2. Retrieve all `MaterialTopic` objects associated with the specified `framework_id`.
    3. Serialize the `MaterialTopic` objects using the `MaterialTopicModelSerializer` and return the serialized data in the response.

    The response will have a status code of 200 OK if the request is successful.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        framework_serializer = CustomFrameworkSerializer(data=request.query_params)
        framework_serializer.is_valid(raise_exception=True)
        framework = framework_serializer.validated_data["framework_id"]
        topics = MaterialTopic.objects.filter(framework=framework)
        serializer = MaterialTopicModelSerializer(topics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
