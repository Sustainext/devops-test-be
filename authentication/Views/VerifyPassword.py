from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from authentication.serializers.VerifyPasswordSerializer import VerifyPasswordSerializer

class VerifyPasswordAPIView(APIView):
    """
    API view to verify if a submitted password matches the authenticated user's password.

    This can be used for password confirmation before performing sensitive operations.

    Returns:
        - 200 OK with {"valid": true} if password is correct
        - 400 Bad Request with {"valid": false, "message": "..."} if password is incorrect
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VerifyPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"valid": False, "message": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        password = serializer.validated_data["password"]
        user = request.user

        # Check if the password is correct
        if user.check_password(password):
            return Response({"valid": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"valid": False, "message": "Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST
            )
