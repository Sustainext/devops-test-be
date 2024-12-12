from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class SustainappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sustainapp"


class UserActivationEmail(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sustainapp"

    def ready(self):
        import sustainapp.signals
