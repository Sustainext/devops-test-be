from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.apps import apps
from sustainapp.Serializers.TaskdashboardRetriveSerializer import CustomUserSerializer


# Extracting the ExtendedUser Model
User = apps.get_model(settings.AUTH_USER_MODEL)


class UserClientViewset(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Retrieves a list of users associated with the current user's client ID.

        This method is part of the `UserClientViewset` class, which is an API view that handles requests related to user-client associations.

        When a user makes a GET request to this endpoint, the method retrieves all users that have the same client ID as the current user. It then serializes the user data using the `CustomUserSerializer` and returns the serialized data in the response.

        """
        user_client = self.request.user.client_id
        users = User.objects.filter(client_id=user_client).select_related("client")
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)
