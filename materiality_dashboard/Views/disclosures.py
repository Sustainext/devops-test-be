from materiality_dashboard.models import Disclosure
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser


class DisclosureViewSet(viewsets.ModelViewSet):
    queryset = Disclosure.objects.all()
    serializer_class = DisclosureSerializer
