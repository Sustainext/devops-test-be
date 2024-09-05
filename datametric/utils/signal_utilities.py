from datametric.utils.climatiq import Climatiq
from datametric.models import DataMetric, RawResponse, DataPoint
import logging
from django.db.models.signals import post_save


logger = logging.getLogger("custom_logger")


def climatiq_data_creation(raw_response: RawResponse):
    """
    This function is called when a raw response is created.
    It creates the climatiq data points.
    """
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
        data_point, created = DataPoint.objects.update_or_create(
            data_metric=data_metric,
            index=index,
            raw_response=raw_response,
            defaults={
                "path": path,
                "response_type": data_metric.response_type,
                "number_holder": number_value,
                "string_holder": string_value,
                "json_holder": json_value,
                "value": value,
                "metric_name": metric_name,
                # "location": raw_response.location,
                "locale": raw_response.locale,
                "corporate": raw_response.corporate,
                "organization": raw_response.organization,
                "year": raw_response.year,
                "month": raw_response.month,
                "user_id": raw_response.user.id,
                "client_id": raw_response.user.client.id,
            },
        )
        data_point.save()

        if created:
            logger.info("DataPoint created")
        else:
            logger.info("DataPoint updated")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


def process_raw_response_data(
    data_point_dict: dict,
    data_metrics,
    index: int,
    raw_response: RawResponse,
):
    for key, value in data_point_dict.items():
        data_metric,_ = DataMetric.objects.get_or_create(name=key,path=raw_response.path,response_type="String")
        create_or_update_data_points(data_metric, value, index, raw_response)

