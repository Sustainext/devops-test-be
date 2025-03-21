from celery import shared_task
from django.db.models import prefetch_related_objects
from datametric.models import DataPoint, EmissionAnalysis, RawResponse
from datametric.utils.process_json_utility import process_json
from analysis.utils.analysis_data_maker import create_analysis_data
import logging

logger = logging.getLogger("celery_logger")


@shared_task
def process_raw_response_task(instance_id):
    """
    Celery task to process RawResponse asynchronously.
    """
    try:
        # Retrieve the instance
        instance = RawResponse.objects.get(id=instance_id)

        # Prefetch related objects
        prefetch_related_objects([instance], "path", "user", "client")

        # Delete old DataPoints & EmissionAnalysis
        DataPoint.objects.filter(raw_response=instance).delete()
        EmissionAnalysis.objects.filter(raw_response=instance).delete()

        # Process JSON and create analysis data
        process_json(instance.data, instance.path, instance)
        create_analysis_data(instance)
        logger.info(f"Processed RawResponse with id {instance_id}")

    except RawResponse.DoesNotExist:
        # Handle case where instance is deleted before task runs
        logger.error(f"RawResponse with id {instance_id} no longer exists.")
