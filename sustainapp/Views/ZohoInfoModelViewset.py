from sustainapp.Serializers.ZohoInfoModelSerializer import ZohoInfoSerializer
from sustainapp.models import ZohoInfo
from rest_framework import viewsets
from sustainapp.Permissions.IsSuperuser import IsSuperuser
from rest_framework.permissions import IsAuthenticated


class ZohoInfoViewset(viewsets.ModelViewSet):
    serializer_class = ZohoInfoSerializer

    def get_queryset(self):
        return ZohoInfo.objects.filter(client=self.request.user.client)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsSuperuser()]
        return [IsAuthenticated()]
