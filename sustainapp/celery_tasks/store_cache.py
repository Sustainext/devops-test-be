from celery import shared_task
from django.core.cache import cache


@shared_task
def store_cache(cache_key, data, timeout=300):
    """
    Store cache asynchronously in Redis using Celery.
    """
    cache.set(cache_key, data, timeout)
