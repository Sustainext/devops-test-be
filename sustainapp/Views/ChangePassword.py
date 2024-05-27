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
        user = self.request.user
        try:
            has_login_first = LoginCounter.objects.get(user=user).login_counter != 1
            if has_login_first:
                raise ValidationError(
                    "User has not logged in first", code="not_logged_in"
                )
        except LoginCounter.DoesNotExist:
            raise ValidationError("User has not logged in first", code="not_logged_in")
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password1 = serializer.validated_data["password1"]
        password2 = serializer.validated_data["password2"]
        # Check if passwords match
        if password1 != password2:
            # Raise error if passwords don't match
            raise ValidationError("Passwords do not match", code="password_mismatch")
        else:
            user.set_password(password1)
            user.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
