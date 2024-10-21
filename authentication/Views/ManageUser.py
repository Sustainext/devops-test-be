from authentication.serializers.ManageUserSerializer import ManageUserSerializer
from rest_framework import viewsets
from authentication.models import CustomUser
from rest_framework.response import Response
from rest_framework import status


class ManageUserViewSet(viewsets.ModelViewSet):
    serializer_class = ManageUserSerializer

    def get_queryset(self):
        client_id = self.request.user.client.id
        queryset = CustomUser.objects.filter(client_id=client_id)
        return queryset

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "POST method is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
