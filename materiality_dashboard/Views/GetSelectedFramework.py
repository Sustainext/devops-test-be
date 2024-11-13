from sustainapp.models import Framework, Userorg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.serializers import FrameworkSerializer


class GetSelectedFramework(APIView):
    """
    Provides an API view to retrieve the frameworks associated with the authenticated user's organizations.

    This view retrieves all the frameworks that are associated with the organizations the authenticated user is a part of.
    The frameworks are serialized using the FrameworkSerializer and returned in the response.

    Returns:
        A list of framework data in JSON format.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        # * Get all the frameworks of organisations that the user is associated with
        frameworks = Framework.objects.filter(
            id__in=(
                Userorg.objects.filter(user=user).values_list(
                    "organization__framework", flat=True
                )
            )
        )
        # * Serialize the frameworks
        serializer = FrameworkSerializer(frameworks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
