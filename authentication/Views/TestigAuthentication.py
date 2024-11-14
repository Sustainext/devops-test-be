from sustainapp.models import Organization
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from authentication.Permissions.IsClientAdmin import IsClientAdmin


class TestAuthentication(APIView):
    permission_classes = [IsClientAdmin]

    def get(self, request):
        print(
            f"User: {request.user}, Is Staff: {request.user.is_staff},Group: {request.user.groups.all()}"
        )
        # Retrieve the organization from the request
        organization = "Some data from the organization"
        # Return the organization as a response
        return Response(organization, status=status.HTTP_200_OK)
