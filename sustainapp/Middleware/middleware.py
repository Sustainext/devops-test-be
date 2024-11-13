from sustainapp.models import Client
from django.utils.deprecation import MiddlewareMixin
import jwt
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger("django")


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            "/api/auth/password/reset/",
            "/api/auth/password-reset/confirm/",
        ]

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if not any(request.path.startswith(path) for path in self.exempt_paths):
            if auth_header:
                try:
                    token = auth_header.split(" ")[1]
                    with open("public_key.pem", "r") as key_file:
                        public_key = key_file.read()
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                    )
                    client = payload.get("client_id")
                    if not client:
                        raise PermissionDenied("Cient Not Found")
                    client = Client.objects.get(id=client)
                    request.client = client

                except jwt.DecodeError:
                    raise PermissionDenied("Error in Token .Access Denied")
                except jwt.ExpiredSignatureError:
                    raise PermissionDenied("Token has expired Access Denied")
                except Client.DoesNotExist:
                    raise PermissionDenied("Client Not Found")

        response = self.get_response(request)
        return response


class MITMDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("Checking for MITM")
        logger.info(request.headers)
        # Allow localhost
        if request.get_host().startswith("127.0.0.1") or request.get_host().startswith(
            "localhost"
        ):
            return self.get_response(request)

        # Check for secure connection
        if not request.is_secure():
            return HttpResponseForbidden("HTTPS Required")

        response = self.get_response(request)
        return response


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the last activity time from session
        last_activity = request.session.get("last_activity")
        if last_activity:
            now = timezone.now()
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            if now - last_activity_time > timedelta(
                seconds=settings.SESSION_COOKIE_AGE
            ):
                # Timeout, log out the user
                from django.contrib.auth import logout

                logout(request)

        # Update last activity time
        request.session["last_activity"] = timezone.now().isoformat()

        response = self.get_response(request)
        return response


class SecureCookiesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for cookie in response.cookies.values():
            cookie.secure = True
            cookie.httponly = True
        return response
