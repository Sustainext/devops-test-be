from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
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
        #* Cache User Password for faster verification
        if cache.get(f"password_{user.id}") is None:
            cache.set(f"password_{user.id}", user.password, timeout=30)

        # Check if the password is correct
        if check_password(password, cache.get(f"password_{user.id}")):
            return Response({"valid": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"valid": False, "message": "Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST
            )
