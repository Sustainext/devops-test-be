from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from authentication.serializers.CustomUserSerializer import CustomUserSerializer
from authentication.serializers.CustomUserListSerializer import CustomUserListSerializer
CustomUser = get_user_model()

class CreateCustomUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Create a mutable copy of the request data
        print(request.body, ' is the request')
        mutable_data = request.data.copy()

        # Set the client to be the same as the requesting user's client
        mutable_data['client'] = request.user.client.id
        print(mutable_data, ' is mutable data')
        serializer = CustomUserSerializer(data=mutable_data)
        if serializer.is_valid():
            # Create the user instance
            user = serializer.save()

            # Set additional fields that might not be part of the serializer
            user.is_client_admin = False
            user.admin = False
            user.roles = "employee"  # Default role
            user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class CheckUserExistsView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        email = request.query_params.get('email')

        if not username and not email:
            return Response(
                {"error": "Please provide either username or email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {}

        if username:
            username_exists = CustomUser.objects.filter(username__iexact=username).exists()
            response_data['username_taken'] = username_exists

        if email:
            email_exists = CustomUser.objects.filter(email__iexact=email).exists()
            response_data['email_taken'] = email_exists

        return Response(response_data)



class ClientUsersListView(APIView):

    def get(self, request):
        # Get the client of the logged-in user
        client = request.user.client

        # Query all users with the same client
        users = CustomUser.objects.filter(client=client)

        # Serialize the users
        serializer = CustomUserSerializer(users, many=True)

        return Response(serializer.data)

