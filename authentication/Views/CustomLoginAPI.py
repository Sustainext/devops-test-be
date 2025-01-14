from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from authentication.utils import (
    handle_failed_login,
    reset_failed_login_attempts,
)


class CustomLoginView(LoginView):
    def get_response(self):
        """Customizing token response format with claims and token_type
        Remember me parameter for making longer validity token, so that we can save it on storage/cookie
        long_validity_request parameter for devs only
        Added client uuid for frontend access"""

        user = self.user

        remember_me = self.request.data.get("remember_me", False)

        refresh = RefreshToken.for_user(user)

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

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=request.data)
        user_model = get_user_model()

        # Check if the user exists
        username = request.data.get("username")
        if not user_model.objects.filter(username__iexact=username).exists():
            return Response(
                {
                    "message": "Account doesn't exist with the provided email or username."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if user_model.objects.filter(
            username__iexact=request.data.get("username"),
            is_active=False,
        ).exists():
            return Response(
                {"message": "Your account is deactivated. Please contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not self.serializer.is_valid():
            user = user_model.objects.filter(
                username__iexact=request.data.get("username")
            ).first()
            if user:
                safelock = handle_failed_login(user)
                if safelock.is_locked:
                    if safelock.locked_at and (
                        timezone.now() - safelock.locked_at >= timedelta(hours=2)
                    ):
                        safelock.is_locked = False
                        safelock.failed_login_attempts = 0
                        safelock.locked_at = None
                        safelock.last_failed_at = None
                        safelock.save()
                    else:
                        return Response(
                            {
                                "message": "Your account has been locked due to multiple failed login attempts. "
                                "Please reset your password or contact the support team.",
                            },
                            status=status.HTTP_403_FORBIDDEN,
                        )

            return Response(
                {"message": "Incorrect username or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log in the user
        self.login()
        user = self.user

        if user.safelock.is_locked:
            if user.safelock.locked_at and (
                timezone.now() - user.safelock.locked_at >= timedelta(hours=2)
            ):
                user.safelock.is_locked = False
                user.safelock.failed_login_attempts = 0
                user.safelock.locked_at = None
                user.safelock.last_failed_at = None
                user.safelock.save()
            else:
                return Response(
                    {
                        "message": "Your account has been locked due to multiple failed login attempts. "
                        "Please reset your password or contact the support team.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        reset_failed_login_attempts(user)
        return self.get_response()
