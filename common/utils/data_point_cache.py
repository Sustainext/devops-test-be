from django.core.cache import cache
from datametric.models import DataPoint
import logging

logger = logging.getLogger(__name__)


def set_data_point_cache(data_point):
    data_point_dictionary = {
        "id": data_point.id,
        "raw_response_id": data_point.raw_response.id,
        "index": data_point.index,
        "data_metric_name": data_point.data_metric.name,
        "value": data_point.value,
        "location_name": data_point.location.name
    }
    cache.set(f"data_point_{data_point.id}", data_point_dictionary, timeout=None)


def get_data_point_cache(data_point_id):
    if cache.get(f"data_point_{data_point_id}") is None:
        try:
            data_point = DataPoint.objects.get(id=data_point_id)
            set_data_point_cache(data_point)
        except DataPoint.DoesNotExist:
            pass
    return cache.get(f"data_point_{data_point_id}")


def delete_data_point_cache(data_point_id):
    cache.delete(f"data_point_{data_point_id}")


def delete_multiple_data_point_cache(data_point_ids):
    for data_point_id in data_point_ids:
        delete_data_point_cache(data_point_id)
