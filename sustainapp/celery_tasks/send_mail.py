from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from sustainapp.models import ClientTaskDashboard
import time
from logging import getLogger

logger = getLogger("celery_logger")


@shared_task(rate_limit="20/m")  # Limit to 20 emails per minute for all workers
def async_send_email(subject, template_name, recipient_email, context):
    """Celery task to send an email asynchronously."""
    html_message = render_to_string(template_name, context)
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        list(recipient_email)
        if isinstance(recipient_email, (list, tuple))
        else [recipient_email],  # Ensure a flat list
        html_message=html_message,
    )


@shared_task(rate_limit="1/s")  # Limit to 1 email per second for all workers
def send_bulk_task_emails(task_ids):
    """
    Celery task that sends emails for multiple tasks in a single execution.
    task_ids: List of task IDs that need email notifications.
    """
    for task_id in task_ids:
        try:
            # Fetch task details
            task = ClientTaskDashboard.objects.get(pk=task_id)

            if task.assigned_to:
                first_name = task.assigned_to.first_name.capitalize()
                task_name = task.task_name
                platform_link = settings.EMAIL_REDIRECT
                recipient_email = task.assigned_to.email

                subject = "New Emission Task Assigned"
                template_name = "sustainapp/task_assigned.html"
                context = {
                    "task_id": task.pk,
                    "first_name": first_name,
                    "task_name": task_name,
                    "platform_link": platform_link,
                    "deadline": task.deadline,
                    "assigned_by": task.assigned_by.first_name.capitalize(),
                    "location": task.location.name if task.location else None,
                    "category": task.category,
                    "subcategory": task.subcategory,
                    "scope": task.scope,
                    "month": task.month,
                    "year": task.year,
                }

                logger.info(
                    f"Sending Email for Task ID: {task.pk} to {recipient_email}"
                )  # Debugging

                html_message = render_to_string(template_name, context)
                send_mail(
                    subject,
                    "",
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    html_message=html_message,
                )
                time.sleep(1)  # Add 1 second delay to avoid rate limiting

        except ClientTaskDashboard.DoesNotExist:
            logger.info(f"Task ID {task_id} not found")  # Log if task ID is missing


@shared_task(rate_limit="1/s")  # Limit to 1 email per second for all workers
def send_bulk_approved_and_reject_emails(task_ids):
    for task_id in task_ids:
        try:
            # Fetch task details
            task = ClientTaskDashboard.objects.get(pk=task_id)

            if task.assigned_to:
                first_name = task.assigned_to.first_name.capitalize()
                task_name = task.task_name
                platform_link = settings.EMAIL_REDIRECT
                recipient_email = task.assigned_to.email
                subject = "Emission Task Approved"
                template_name = "sustainapp/task_approved.html"
                context = {
                    "first_name": first_name,
                    "task_name": task_name,
                    "platform_link": platform_link,
                }

                logger.info(
                    f"Sending Email for Task ID: {task.pk} to {recipient_email}"
                )  # Debugging

                html_message = render_to_string(template_name, context)
                send_mail(
                    subject,
                    "",
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    html_message=html_message,
                )
                time.sleep(1)  # Delay each email by 1 second

        except ClientTaskDashboard.DoesNotExist:
            logger.info(f"Task ID {task_id} not found")
