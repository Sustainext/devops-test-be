from datametric.utils.climatiq import Climatiq
from datametric.models import DataMetric, RawResponse, DataPoint
import logging
from django.db.models.signals import post_save
from logging import getLogger


logger = getLogger("file")


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
        # Retrieve existing data point if it exists
        existing_data_point = DataPoint.objects.filter(
            data_metric=data_metric, index=index
        ).first()

        # Check existing value for comparison
        existing_value = None
        if existing_data_point:
            if data_metric.response_type == "String":
                existing_value = existing_data_point.string_holder
            elif data_metric.response_type in ["Integer", "Float"]:
                existing_value = existing_data_point.number_holder
            elif data_metric.response_type in ["Array Of Objects", "Object"]:
                existing_value = existing_data_point.json_holder
            elif data_metric.response_type == "Boolean":
                existing_value = (
                    existing_data_point.boolean_holder
                )  # Assuming you have a boolean_holder field

        # Create or update the data point
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
                "boolean_holder": boolean_value,
            },
        )

        # Save the updated or created data point
        data_point.save()
        # print('User role is ',raw_response.user.custom_role )
        # Log only if there is a change in the value
        if created or (existing_value != value):
            logger.info("DataPoint created/updated with changes")
        else:
            # pass
            logger.info("DataPoint updated without changes")

            # Upload logs only when there is a change
            # uploader.upload_logs(log_data)

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
    print(raw_response, " &&&& is the raw response")
    for key, value in data_point_dict.items():
        try:
            data_metric = DataMetric.objects.get(name=key, path=raw_response.path)
        except DataMetric.DoesNotExist:
                data_metric = DataMetric.objects.create(
                    name=key, 
                    path=raw_response.path, 
                    response_type="String"
                )
                data_metric.save()
        except DataMetric.MultipleObjectsReturned:
            data_metrics = DataMetric.objects.filter(name=key, path=raw_response.path)
            if data_metrics.filter(response_type="String").exists():
                data_metrics_to_keep = data_metrics.filter(response_type="String").last()
                data_metrics.exclude(id=data_metrics_to_keep.id).delete()
                data_metric = data_metrics_to_keep
            #* What if other than string duplicate datametrics are there?
            
        create_or_update_data_points(data_metric, value, index, raw_response)
