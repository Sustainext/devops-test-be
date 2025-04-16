from django.core.cache import cache
from datametric.models import DataPoint
import logging

logger = logging.getLogger('celery_logger')


def set_data_point_cache(data_point):
    """
    Sets the cache for a given data point.
    """
    data_point_dictionary = {
        "id": data_point.id,
        "raw_response_id": data_point.raw_response.id,
        "index": data_point.index,
        "data_metric_name": data_point.data_metric.name,
        "value": data_point.value,
        "location_name": data_point.locale.name if data_point.locale else None
    }
    logger.info(data_point_dictionary)
    cache.set(f"data_point_{data_point.id}", data_point_dictionary, timeout=None)


def get_data_point_cache(data_point_id):
    """
    Retrieves the cache for a given data point.
    If the cache is not found, it will be set.
    """
    if cache.get(f"data_point_{data_point_id}") is None:
        try:
            data_point = DataPoint.objects.get(id=data_point_id)
            set_data_point_cache(data_point)
        except DataPoint.DoesNotExist:
            pass
    return cache.get(f"data_point_{data_point_id}")


def delete_data_point_cache(data_point_id):
    """
    Deletes the cache for a given data point.
    """
    cache.delete(f"data_point_{data_point_id}")


def delete_multiple_data_point_cache(data_point_ids):
    """
    Deletes the cache for multiple data points.
    """
    for data_point_id in data_point_ids:
        logger.info(f"Deleting data point cache for id: {data_point_id}")
        delete_data_point_cache(data_point_id)
