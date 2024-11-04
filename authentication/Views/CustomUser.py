from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from authentication.serializers.CustomUserSerializer import CustomUserSerializer
from authentication.serializers.CustomUserListSerializer import CustomUserListSerializer
from sustainapp.models import Userorg, Organization

CustomUser = get_user_model()


class CreateCustomUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mutable_data = request.data.copy()
        mutable_data["client"] = request.user.client.id
        organization_ids = mutable_data.get("orgs", [])

        serializer = CustomUserSerializer(data=mutable_data)

        if serializer.is_valid():

            user = serializer.save()

            # Set additional fields
            user.client = request.user.client
            user.is_client_admin = False
            user.admin = False

            # Validate and set roles: only "manager" or "employee" are allowed
            allowed_roles = ["manager", "employee"]
            user.roles = mutable_data.get("roles", "employee")
            if user.roles not in allowed_roles:
                user.roles = "employee"

            user.save()
            # Add a new email address to user.emailaddress_set
            email_address = user.emailaddress_set.create(
                email=mutable_data.get(
                    "email"
                ),  # Assuming 'email' is in the request data
                primary=True,  # Set the email as the primary email
                verified=True,  # Initially set as unverified
            )
            if organization_ids:
                # Create or retrieve Userorg instance
                userorg, created = Userorg.objects.get_or_create(
                    user=user, client=user.client
                )

                # Fetch organizations based on provided IDs
                organizations = Organization.objects.filter(id__in=organization_ids)

                # Link organizations to the Userorg instance
                userorg.organization.set(organizations)
                userorg.save()

            return Response(
                {"message": "User Created Successfully"}, status=status.HTTP_201_CREATED
            )

        # Return validation errors if the serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUserExistsView(APIView):
    def get(self, request):
        username = request.query_params.get("username")
        email = request.query_params.get("email")

        if not username and not email:
            return Response(
                {"error": "Please provide either username or email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = {}

        if username:
            username_exists = CustomUser.objects.filter(
                username__iexact=username
            ).exists()
            response_data["username_taken"] = username_exists

        if email:
            email_exists = CustomUser.objects.filter(email__iexact=email).exists()
            response_data["email_taken"] = email_exists

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
