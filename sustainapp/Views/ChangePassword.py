from rest_framework.views import APIView
from rest_framework.response import Response
from sustainapp.models import LoginCounter
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from sustainapp.Serializers.ChangePasswordSerializer import ChangePasswordSerializer
from rest_framework import status


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password1 = serializer.validated_data["password1"]
        password2 = serializer.validated_data["password2"]

        if password1 != password2:
            raise ValidationError("Passwords do not match", code="password_mismatch")

        request.user.set_password(password1)
        request.user.save()
        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )
