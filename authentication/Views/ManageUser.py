from authentication.serializers.ManageUserSerializer import ManageUserSerializer
from rest_framework import viewsets
from authentication.models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from authentication.Permissions.IsAdmin import IsAdmin
from django.db.models import ProtectedError


class ManageUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
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

    def perform_destroy(self, instance):
        related_fields = instance._meta.get_fields()
        
        for field in related_fields:
                try:
                    return super().perform_destroy(instance)
                except ProtectedError as e:
                    # Handle protected objects by force deleting them
                    protected_objects = e.protected_objects
                    for protected_obj in protected_objects:
                        protected_obj.delete()
                        
        return super().perform_destroy(instance)