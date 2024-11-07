# views.py
import requests
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from utils.auth0 import validate_id_token  # Add this helper function for token validation

class Auth0LoginView(APIView):
    """Login view for Auth0 users"""

    def post(self, request):
        id_token = request.data.get('id_token')

        if not id_token:
            return Response({"error": "ID token is required"}, status=400)

        try:
            # Validate the ID token using Auth0
            user_data = validate_id_token(id_token)
            user = self.get_or_create_user(user_data)  # Get or create the user in your DB
            
            # Use simple-jwt to create refresh and access tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Customize token expiration based on remember_me
            remember_me = request.data.get("remember_me", False)
            if remember_me:
                refresh.set_exp(lifetime=timedelta(days=30))
                access_token.set_exp(lifetime=timedelta(days=30))
            else:
                access_token.set_exp(lifetime=timedelta(hours=1))

            # Add client_id and roles to the tokens
            refresh["client_id"] = user.client.id
            access_token["client_id"] = user.client.id

            # Format expiration times for readable output
            access_exp_readable = access_token["exp"]
            refresh_exp_readable = refresh["exp"]

            data = {
                "token_type": "bearer",
                "access": str(access_token),
                "refresh": str(refresh),
                "access_exp": access_token["exp"],
                "access_exp_readable": access_exp_readable,
                "refresh_exp": refresh["exp"],
                "refresh_exp_readable": refresh_exp_readable,
            }

            # Return response
            response = Response({
                "key": data,
                "client_key": user.client.uuid,
                "role": user.roles,
                "permissions": user.permissions,
            }, status=200)

            # Set tokens in cookies
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
            return Response({"error": str(e)}, status=400)
