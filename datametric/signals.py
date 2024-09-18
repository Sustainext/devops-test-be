from django.db.models.signals import post_save
from django.dispatch import receiver
from datametric.models import RawResponse, DataPoint, DataMetric, EmissionAnalysis
from django.db.models import prefetch_related_objects
from datametric.utils.signal_utilities import (
    process_raw_response_data,
)
from datametric.utils.signal_utilities import climatiq_data_creation
from analysis.utils.analysis_data_maker import create_analysis_data
from logging import getLogger

logger = getLogger("django.log")


def process_json(json_obj, path, raw_response):
    print("process_json - hit")
    print("path is ", path.slug)
    data_metrics = DataMetric.objects.filter(path=path)
    for index, item in enumerate(json_obj):
        print(item)
        if isinstance(item, dict):
            try:
                first_key, first_value = next(iter(item.items()))
                # Print the first key and value
                print(f"Field Group Row: {first_key}")
                print(f"First Value: {first_value}")
                """
                This was required since emissions has different
                data structure in RawResponse data field when
                compared to other environment modules.
                """
                if type(first_value) in [
                    int,
                    str,
                    bool,
                ]:

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
                    return None
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
    if raw_response.data != [{}]:
        climatiq_data_creation(raw_response=raw_response)
    else:
        logger.error(
            "Signals.py file, when checked for rawresponse.data it has No data added."
        )


@receiver(post_save, sender=RawResponse)
def create_response_points(sender, instance: RawResponse, created, **kwargs):
    prefetch_related_objects([instance], "path", "user", "client")
    DataPoint.objects.filter(raw_response=instance).delete()
    EmissionAnalysis.objects.filter(raw_response=instance).delete()
    # No matter, whether it is getting created or updated, this should be run.
    #! Don't save the instance again, goes to non stop recursion.

    process_json(instance.data, instance.path, instance)
    create_analysis_data(instance)
