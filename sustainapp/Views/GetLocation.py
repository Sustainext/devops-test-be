from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.GetLocationSerializer import GetLocationSerializer


class LocationListAPIView(ListAPIView):
    """
    List all locations of a user with caching.
    Cache should be cleared if the user's location permissions change.
    """

    serializer_class = GetLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_cache_key(self):
        """Generate a cache key AFTER authentication is applied"""
        user_id = getattr(self.request.user, "id", None)
        if user_id is None:
            return "anonymous_locations"
        return f"user_{user_id}_locations"

    def get_queryset(self):
        """Return locations for the authenticated user."""
        return self.request.user.locs.filter(client=self.request.client)

    def finalize_response(self, request, response, *args, **kwargs):
        """Handles caching AFTER the response has been fully processed."""
        response = super().finalize_response(request, response, *args, **kwargs)

        cache_key = self.get_cache_key()
        if cache_key != "anonymous_locations":
            if hasattr(response, "render") and callable(response.render):
                response.render()
            cache.set(cache_key, response, 60 * 5)

        return response
