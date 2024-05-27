from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers.CustomLoginSerializers import (
    CustomTokenObtainPairSerializer,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes


class CustomLoginView(LoginView):
    """Over-riding the Default Login View"""

    def get_response(self):
        """Adding client id to tokens sent during login"""
        user = self.user
        refresh = RefreshToken.for_user(user)
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        data = {
            "refresh": str(token),
            "access": str(token.access_token),
        }
        return Response({"key": data}, status=200)
