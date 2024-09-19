from dj_rest_auth.views import LogoutView
from rest_framework.response import Response


class CustomLogoutView(LogoutView):
    """Over-riding the Default Logout View"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        response.data = {"message": "Logged out successfully"}
        return response