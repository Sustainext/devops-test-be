from django.db.models.signals import post_save
from django.dispatch import receiver
from datametric.models import RawResponse
from datametric.Tasks.RawResponseTask import process_raw_response_task
from django.db import transaction


@receiver(post_save, sender=RawResponse)
def create_response_points(sender, instance: RawResponse, created, **kwargs):
    """
    Signal that triggers a Celery task whenever a RawResponse is saved.
    """
    # Call the Celery task instead of running the logic directly
    transaction.on_commit(lambda: process_raw_response_task.delay(instance.id))
