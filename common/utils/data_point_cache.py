from django.core.cache import cache
from datametric.models import DataPoint


def set_data_point_cache(data_point):
    cache.set(f"data_point_{data_point.id}", data_point, timeout=None)


def get_data_point_cache(data_point_id):
    if cache.get(f"data_point_{data_point_id}") is None:
        try:
            data_point = DataPoint.objects.get(id=data_point_id)
            set_data_point_cache(data_point)
        except DataPoint.DoesNotExist:
            return None
    return cache.get(f"data_point_{data_point_id}")


def delete_data_point_cache(data_point_id):
    cache.delete(f"data_point_{data_point_id}")


def delete_multiple_data_point_cache(data_point_ids):
    for data_point_id in data_point_ids:
        delete_data_point_cache(data_point_id)
