from datametric.models import DataMetric
from datametric.utils.signal_utilities import (
    process_raw_response_data,
)
from datametric.utils.PathsForDataPoints import (
    all_type_paths,
)
from datametric.utils.CreateDataPoints import CreateDataPointsClass
from logging import getLogger

logger = getLogger("django.log")


def process_json(json_obj, path, raw_response):
    data_metrics = DataMetric.objects.filter(path=path)

    # Create DataPoints for RawResponse where it's failing to create DataPoints
    if path.slug in all_type_paths:
        create_dp_obj = CreateDataPointsClass(
            json_obj, path, raw_response, data_metrics
        )
        create_dp_obj.create_data_points_for_raw_response()
    else:
        for index, item in enumerate(json_obj):
            if isinstance(item, dict):
                try:
                    first_key, first_value = next(iter(item.items()))
                    # Print the first key and value
                    # print(f"Field Group Row: {first_key}")
                    # print(f"First Value: {first_value}")
                    """
                    This was required since emissions has different
                    data structure in RawResponse data field when
                    compared to other environment modules.
                    """
                    if type(first_value) in [int, str, bool, type(None)]:
                        process_raw_response_data(
                            data_point_dict=item,
                            data_metrics=data_metrics,
                            index=index,
                            raw_response=raw_response,
                        )
                    elif isinstance(first_value, list):
                        for data_point in first_value:
                            if isinstance(data_point, dict):
                                process_raw_response_data(
                                    data_point_dict=data_point,
                                    data_metrics=data_metrics,
                                    index=index,
                                    raw_response=raw_response,
                                )
                    else:
                        process_raw_response_data(
                            data_point_dict=first_value,
                            data_metrics=data_metrics,
                            index=index,
                            raw_response=raw_response,
                        )
                except StopIteration:
                    logger.error(
                        f"Warning: Empty dictionary encountered at index {index} and path {path}.So skipping."
                    )
                    continue
            else:
                logger.error(
                    f"Warning:The item must be a Dictionary to proceed with the signals. Invalid data type encountered at index {index} and path {path}.So skipping."
                )
                continue