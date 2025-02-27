from django.core.cache import cache
from celery import shared_task


@shared_task
def clear_user_location_cache(user_id):
    """Clears the cache for a specific user's locations"""
    cache_key = f"user_{user_id}_locations"
    cache.delete(cache_key)
