from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class GetUserRoles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        roles = user.roles
        custom_role = user.custom_role.name if user.custom_role else None
        admin = user.admin
        return Response(
            {"roles": roles, "custom_role": custom_role, "admin": admin},
            status=status.HTTP_200_OK,
        )
