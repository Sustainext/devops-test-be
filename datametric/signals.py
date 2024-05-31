from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RawResponse, ResponsePoint, DataPoint



def process_json(json_obj, instance):
    print('process_json - hit')
    data_points = DataPoint.objects.filter(path=path)
    for item in json_obj:
            if isinstance(item, dict):
                first_key, first_value = next(iter(item.items()))
                # Print the first key and value
                print(f"First Key: {first_key}")
                print(f"First Value: {first_value}")
                path = instance.path
                for key, value in first_value.items():
                    print(f"Key: {key}, Value: {value}")



@receiver(post_save, sender=RawResponse)
def create_response_points(sender, instance, created, **kwargs):
    if created:
        # Example logic to create response points
        data_points = DataPoint.objects.filter(path=instance.path)
        print('this is from the signals - creation')
        print(instance.path, instance.data, instance.user, instance.client)
        process_json(instance.data)
        # for data_point in data_points:
        #     ResponsePoint.objects.create(
        #         path=instance.path,
        #         raw_response=instance,
        #         data_point=data_point,
        #         response_type='String',  # Set default or custom logic
        #         string_holder='default value',  # Set based on your requirements
        #     )
    else:
        print('this is from the signals - updation')
        print(instance.path, instance.data, instance.user, instance.client)
        process_json(instance.data)

