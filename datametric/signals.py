from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RawResponse, ResponsePoint, DataPoint


def createOrUpdateResponsePoints(data_point, value, path, index, location, year, month, client, user):
    print('Creating or updating Data points')

# class ResponsePoint(AbstractModel):
#     path = models.ForeignKey(Path, on_delete=models.PROTECT)
#     raw_response = models.ForeignKey(
#         RawResponse,
#         on_delete=models.PROTECT,
#         default=None,
#         related_name="response_points",
#     )
#     response_type = models.CharField(
#         max_length=20, choices=DATA_TYPE_CHOICES, default="String"
#     )
#     number_holder = models.FloatField(default=None, null=True)
#     string_holder = models.CharField(default=None, null=True)
#     json_holder = models.JSONField(default=None, null=True)
#     data_point = models.ForeignKey(
#         DataPoint, on_delete=models.PROTECT, default=None, related_name="data_points"
#     )
#     value = models.JSONField(default=None, null=True)

def process_json(json_obj, path):
    print('process_json - hit')
    print('path is ', path.slug)
    data_points = DataPoint.objects.filter(slug=path.slug)
    for point in data_points:
         print(point.name, ' - is a datapoint found')
    for item in json_obj:
            if isinstance(item, dict):
                first_key, first_value = next(iter(item.items()))
                # Print the first key and value
                print(f"First Key: {first_key}")
                print(f"First Value: {first_value}")
                try:
                    for key, value in first_value.items():
                        data_point = data_points.filter(name=key).first()
                        print(data_point,data_point.response_type, ' match found ... ')
                        print(f"for Key: {key}, Value: {value}")

                except KeyError as e:
                    print(f"KeyError: {e}")
                except IndexError as e:
                    print(f"IndexError: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

@receiver(post_save, sender=RawResponse)
def create_response_points(sender, instance, created, **kwargs):
    if created:
        # Example logic to create response points
        print('this is from the signals - creation')
        print(instance.path, instance.data, instance.user, instance.client)
        process_json(instance.data, instance.path)
    else:
        print('this is from the signals - updation')
        print(instance.path, instance.data, instance.user, instance.client)
        process_json(instance.data, instance.path)

