from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.GetLocationSerializer import GetLocationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class LocationListAPIView(ListAPIView):
    """
    List all locations of a user with caching
    """

    serializer_class = GetLocationSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 5))  # Cache the response for 5 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return self.request.user.locs.filter(client=self.request.client)
