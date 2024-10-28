from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers.CustomLoginSerializers import (
    CustomTokenObtainPairSerializer,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from datetime import timedelta, datetime


class CustomLoginView(LoginView):

    def get_response(self):
        """Customizing token response format with claims and token_type
        Remember me parameter for making longer validity token, so that we can save it on storage/cookie
        long_validity_request parameter for devs only
        Added client uuid for frontend access"""

        user = self.user

        remember_me = self.request.data.get("remember_me", False)
        # Use the CustomTokenObtainPairSerializer to generate tokens
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)

        refresh = RefreshToken.for_user(user)

        if remember_me:
            """Increasing Token validity time for remember me option"""
            refresh.set_exp(lifetime=timedelta(days=30))
            access_token_lifetime = timedelta(hours=1)
        else:
            refresh.set_exp()
            access_token_lifetime = timedelta(days=1)

        long_validity_request = self.request.data.get("long_validity_request")

        if long_validity_request :
            """Tokens for longer validity So that Devs can use it on postman"""
            access_token_lifetime = timedelta(days=30)

        refresh["client_id"] = user.client.id
        access_token = refresh.access_token
        access_token["client_id"] = user.client.id
        client_key = user.client.uuid

        needs_password_reset = 1 if user.first_login.needs_password_change else 0
        access_token.set_exp(lifetime=access_token_lifetime)

        access_exp_readable = datetime.fromtimestamp(access_token["exp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        refresh_exp_readable = datetime.fromtimestamp(refresh["exp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        data = {
            "token_type": "bearer",
            "access": str(access_token),
            "refresh": str(refresh),
            "access_exp": access_token["exp"],
            "access_exp_readable": access_exp_readable,
            "refresh_exp": refresh["exp"],
            "refresh_exp_readable": refresh_exp_readable,
        }

        response = Response(
            {"key": data, "needs_password_reset": needs_password_reset,"client_key":client_key}, status=200
        )

        # Set access and refresh tokens in cookies
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=True,
            expires=access_token["exp"],
            samesite="Lax",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            expires=refresh["exp"],
            samesite="Lax",
        )

        return response
