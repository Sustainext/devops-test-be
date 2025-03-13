from datametric.utils.climatiq import Climatiq
from datametric.models import DataMetric, RawResponse, DataPoint
from logging import getLogger
from django.core.cache import cache

logger = getLogger("django")


def climatiq_data_creation(raw_response: RawResponse):
    """
    This function is called when a raw response is created.
    It creates the climatiq data points.
    """
    if "gri-environment-emissions-301-a-scope-" not in raw_response.path.slug:
        return None
    else:
        climatiq_call = Climatiq(raw_response=raw_response)
        climatiq_call.create_calculated_data_point()


def create_or_update_data_points(
    data_metric: DataMetric, value, index, raw_response: RawResponse
):
    logger.info("Creating or updating Data points")
    logger.info(
        f"{data_metric} {value} {index} {raw_response.path} {raw_response.user}"
    )

    path = raw_response.path

    number_value = None
    json_value = None
    string_value = None
    boolean_value = None
    metric_name = data_metric.name

    if data_metric.response_type == "String":
        string_value = value
    elif data_metric.response_type in ["Integer", "Float"]:
        number_value = value
    elif data_metric.response_type in ["Array Of Objects", "Object"]:
        json_value = value
    elif data_metric.response_type == "Boolean":
        boolean_value = value

    try:
        # Create or update the data point
        data_point = DataPoint.objects.create(
            data_metric=data_metric,
            index=index,
            raw_response=raw_response,
            path=path,
            response_type=data_metric.response_type,
            number_holder=number_value,
            string_holder=string_value,
            json_holder=json_value,
            value=value,
            metric_name=metric_name,
            # location= raw_response.location,
            locale=raw_response.locale,
            corporate=raw_response.corporate,
            organization=raw_response.organization,
            year=raw_response.year,
            month=raw_response.month,
            user_id=raw_response.user.id,
            client_id=raw_response.user.client.id,
            boolean_holder=boolean_value,
        )

        # Save the updated or created data point
        data_point.save()

    except Exception as e:
        # pass
        logger.error(f"An error occurred: {e}", exc_info=True)
        # pass


def process_raw_response_data(
    data_point_dict: dict,
    data_metrics,
    index: int,
    raw_response: RawResponse,
):
    for key, value in data_point_dict.items():
        try:
            data_metric = DataMetric.objects.get(name=key, path=raw_response.path)
        except DataMetric.DoesNotExist:
            data_metric = DataMetric.objects.create(
                name=key, path=raw_response.path, response_type="String"
            )
            data_metric.save()
        except DataMetric.MultipleObjectsReturned:
            # *: Handle the case where multiple data metrics with the same name and path exist in a more optimised way.
            # * I'm ashamed of writing this code. :-(
            # * Hopefully the MultipleObjectsReturned exception gets less and less common in the future.
            data_metrics = DataMetric.objects.filter(name=key, path=raw_response.path)
            if data_metrics.filter(response_type="String").exists():
                data_metrics_to_keep = (
                    data_metrics.filter(response_type="String").order_by("id").first()
                )
                data_metrics_to_delete = data_metrics.exclude(
                    id=data_metrics_to_keep.id
                )
                # * Change mapping of every data point to last data metric
                data_points = DataPoint.objects.filter(
                    data_metric__in=data_metrics_to_delete
                )
                for data_point in data_points:
                    data_point.data_metric = data_metrics_to_keep
                    data_point.save()
                data_metrics_to_delete.delete()
                data_metric = data_metrics_to_keep
        logger.info(
            f"Data metric : {data_metric.name}, Data Metric Type: {data_metric.response_type}, Value: {value}"
        )
        create_or_update_data_points(data_metric, value, index, raw_response)
