import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "azureproject.settings")

# Create Celery instance
app = Celery("azureproject")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
