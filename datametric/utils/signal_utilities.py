from datametric.utils.climatiq import Climatiq
from datametric.models import DataMetric, RawResponse, DataPoint


def create_or_update_data_points(
    data_metric: DataMetric, value, index, raw_response: RawResponse
):
    print("Creating or updating Data points")
    print(data_metric, value, index, raw_response.path, raw_response.user)

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
                "location": raw_response.location,
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
            print("DataPoint created")
        else:
            print("DataPoint updated")
        climatiq_call = Climatiq(raw_response=raw_response)
        climatiq_call.create_calculated_data_point()
    except Exception as e:
        print(f"An error occurred: {e}")


def process_raw_response_data(
    data_point_dict: dict,
    data_metrics,
    index: int,
    raw_response: RawResponse,
):
    for key, value in data_point_dict.items():
        data_metric = data_metrics.filter(name=key).first()
        create_or_update_data_points(data_metric, value, index, raw_response)
