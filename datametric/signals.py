from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RawResponse, DataPoint, DataMetric
from django.db.models import Q
from django.db.models import prefetch_related_objects
from datametric.utils.climatiq import Climatiq

def create_or_update_data_points(
    data_metric: DataMetric, value, index, raw_response: RawResponse
):
    print("Creating or updating Data points")
    print("Just this one",data_metric, value, index, raw_response.path, raw_response.user)

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


def process_json(json_obj, path, raw_response):
    print("process_json - hit")
    print("path is ", path.slug)
    data_metrics = DataMetric.objects.filter(path=path)
    for index, item in enumerate(json_obj):
        if isinstance(item, dict):
            first_key, first_value = next(iter(item.items()))
            # Print the first key and value
            print(f"Field Group Row: {first_key}")
            print(f"First Value: {first_value}")
            if type(first_value) in [int,str,bool] :

                for key, value in item.items():
                    data_metric = data_metrics.filter(name=key).first()
                    if data_metric is not None:
                        create_or_update_data_points(
                            data_metric, value, index, raw_response
                        )
                    else :
                        print(f"There is no datametric found for this path {path}")
            else:
                try:
                    for key, value in first_value.items():
                        data_metric = data_metrics.filter(name=key).first()
                        print(data_metric, data_metric.response_type, "match found ...")
                        print(f"For Index: {index}, Key: {key}, Value: {value}")
                        # For each of the key pass this to function index, key, value, raw_response create a data point
                        # data_point, value, path, index, location, year, month, client, user
                        create_or_update_data_points(
                            data_metric, value, index, raw_response
                        )
                except KeyError as e:
                    print(f"KeyError: {e}")
                except IndexError as e:
                    print(f"IndexError: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            # else :
            #     print(f"The type of the first value is {type(first_value)}")
            #     for item in first_value:
            #         # if                                                        Please continue to write the code here
            #         for key, value in item.items():
            #             data_metric = data_metrics.filter(name=first_key).first()
            #             create_or_update_data_points(data_metric, value, index, raw_response)
            #             print(f"the datametric created with the value {value}")

@receiver(post_save, sender=RawResponse)
def create_response_points(sender, instance:RawResponse, created, **kwargs):
    prefetch_related_objects([instance], "path", "user","client")
    # No matter, whether it is getting created or updated, this should be run.
    #! Don't save the instance again, goes to non stop recursion.
    process_json(instance.data, instance.path, instance)
