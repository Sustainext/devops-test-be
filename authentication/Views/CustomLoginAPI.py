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
    """Over-riding the Default Login View"""

    def get_response(self):
        """Customizing token response format with claims and token_type"""
        user = self.user

        remember_me = self.request.data.get("remember_me", False)
        # Use the CustomTokenObtainPairSerializer to generate tokens
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)

        refresh = RefreshToken.for_user(user)

        if remember_me:
            refresh.set_exp(lifetime=timedelta(seconds=60))
            access_token_lifetime = timedelta(seconds=30)
        else:
            refresh.set_exp()
            access_token_lifetime = timedelta(days=1)

        refresh["client_id"] = user.client.id
        access_token = refresh.access_token
        access_token["client_id"] = user.client.id

        needs_password_reset = 1 if user.first_login.needs_password_change else 0
        access_token.set_exp(lifetime=access_token_lifetime)

        access_exp_readable = datetime.utcfromtimestamp(access_token["exp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        refresh_exp_readable = datetime.utcfromtimestamp(refresh["exp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        data = {
            "token_type": "bearer",
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "access_exp": access_token['exp'],  # Unix timestamp
            "access_exp_readable": access_exp_readable,  # Human-readable
            "refresh_exp": refresh['exp'],  # Unix timestamp
            "refresh_exp_readable": refresh_exp_readable,  # Human-readable
            "claims": {
                "client_id": access_token["client_id"],
            },
        }

        response = Response(
            {"key": data, "needs_password_reset": needs_password_reset}, status=200
        )

        # Set access and refresh tokens in cookies
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,  # Prevent JavaScript access to the cookie
            secure=True,  # Ensure the cookie is only sent over HTTPS
            expires=access_token["exp"],  # Set expiration time
            samesite="Lax",  # Adjust according to your needs (Lax/Strict/None)
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,  # Prevent JavaScript access
            secure=True,  # Ensure the cookie is only sent over HTTPS
            expires=refresh["exp"],  # Set expiration time
            samesite="Lax",  # Adjust based on your application's needs
        )

        return response
