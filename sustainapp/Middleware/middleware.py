from sustainapp.models import Client
from django.utils.deprecation import MiddlewareMixin
import jwt
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.conf import settings


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
                    payload = jwt.decode(
                        token,
                        settings.SECRET_KEY,
                        algorithms=["HS256"],
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


from django.http import HttpResponseForbidden


class MITMDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow localhost
        if request.get_host().startswith("127.0.0.1:8000"):
            return self.get_response(request)

        print(request.get_host())

        # Check for secure connection
        if not request.is_secure():
            return HttpResponseForbidden("HTTPS Required")

        # Check for unexpected headers
        if "X-Forwarded-For" in request.headers:
            return HttpResponseForbidden("Possible MITM detected")

        # Add more checks as needed

        response = self.get_response(request)
        return response
