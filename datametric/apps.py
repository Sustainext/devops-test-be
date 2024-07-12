from django.apps import AppConfig


class DatametricConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "datametric"

    def ready(self):
        import datametric.signals  #
