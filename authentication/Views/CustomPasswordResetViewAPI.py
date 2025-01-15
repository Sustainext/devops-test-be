from dj_rest_auth.views import PasswordResetConfirmView
from ..serializers.CustomPasswordResetSerializer import (
    CustomPasswordResetConfirmSerializer,
)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    serializer_class = CustomPasswordResetConfirmSerializer
