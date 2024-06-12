from sustainapp.models import Location
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.GetLocationSerializer import GetLocationSerializer

class LocationListAPIView(ListAPIView):
    """
    List all locations of a user
    """
    serializer_class = GetLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Location.objects.filter(client=self.request.client)
        return queryset