# views.py
import requests
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from authentication.Views.auth0 import validate_id_token
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
error_logger = logging.getLogger('custom_logger')

class Auth0LoginView(APIView):
    """Login view for Auth0 users"""

    permission_classes = [AllowAny]

    def get_user(self, email):
        User = get_user_model()
        try:
            user = User.objects.get(username=email)
            return user
        except User.DoesNotExist:
            raise ValidationError("User does not exist with that email.")

    def post(self, request):
        id_token = request.data.get("id_token")

        if not id_token:
            return Response({"error": "ID token is required"}, status=400)

        try:
            # Validate the ID token using Auth0
            user_data = validate_id_token(id_token)
            user = self.get_user(
                user_data["email"]
            )  # Get or create the user in your DB

            # Use simple-jwt to create refresh and access tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Customize token expiration based on remember_me
            remember_me = request.data.get("remember_me", False)
            if remember_me:
                """Increasing Token validity time for remember me option"""
                refresh.set_exp(lifetime=timedelta(days=30))
                access_token_lifetime = timedelta(hours=1)
            else:
                refresh.set_exp()
                access_token_lifetime = timedelta(days=1)

            long_validity_request = self.request.data.get("long_validity_request")

            if long_validity_request:
                """Tokens for longer validity So that Devs can use it on postman"""
                access_token_lifetime = timedelta(days=30)

            refresh["client_id"] = user.client.id
            access_token = refresh.access_token
            access_token["client_id"] = user.client.id
            client_key = user.client.uuid

            needs_password_reset = 0
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
            roles = user.roles
            custom_role = user.custom_role.name if user.custom_role else None
            admin = user.admin
            permissions = {
                "collect": user.collect,
                "analyse": user.analyse,
                "report": user.report,
                "optimise": user.optimise,
                "track": user.track,
            }

            response = Response(
                {
                    "key": data,
                    "needs_password_reset": needs_password_reset,
                    "client_key": client_key,
                    "role": roles,
                    "custom_role": custom_role,
                    "admin": admin,
                    "permissions": permissions,
                },
                status=200,
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

        except ValueError as e:
            error_logger.error(f"Error occurred during login: {e}", exc_info=True)
            return Response({"error": str(e)}, status=400)
