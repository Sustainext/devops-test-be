from sustainapp.models import Client
from django.utils.deprecation import MiddlewareMixin
import jwt
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.conf import settings

# class JWTMiddleware(MiddlewareMixin):
#     def process_request(self,request):
#         auth_header = request.headers.get('Authorization')
#         print("auth_header",auth_header)
#         if auth_header:
#             try:
#                 print("middlesware")
#                 token=auth_header.split(' ')[1]
#                 print("token",token)
#                 payload = jwt.decode(token, '7b4e0d1d203dba17b0e915d77dc83538bb82ebf3c1a2c4606375c23dc0e7267c',algorithms=["HS256"])
#                 print("payload",payload)
#                 client=payload.get('client_id')
#                 print("client",client)
#                 if not client:
#                     raise PermissionDenied("Cient Not Found")
#                 client = Client.objects.get(id=client)
#                 request.client=client

#             except jwt.DecodeError :
#                 return PermissionDenied("Error in Token .Access Denied")
#             except jwt.ExpiredSignatureError:
#                 raise PermissionDenied("Token has expired Access Denied")
#             except Client.DoesNotExist:
#                 raise PermissionDenied("Client Not Found")
#         # else:
#         #     raise PermissionDenied("Authorized Header not provided")


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
                    # print("middlesware")
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
